#! /usr/bin/env python3
"""

terraform init
terraform plan -out plan.out && terraform show -json plan.out ><plan JSON file name>

export DIVVY_API_KEY=<DivvyCloud API Key>
./api_test.py <Divvy base URL> <configuration name> <plan JSON file name>\
    --scan_name=<scan display name to show in scan listing>\
    --author=<scan display name to show in scan listing>\
    --html_out=<HTML output file name>\
    --json_out=<HTML output file name>
    # --auth_for_submission  # only required if your DivvyCloud IaC
                             # installation requires auth


This script is designed to be used in a CI/CD pipeline to make requests to the
DivvyCloud IaC Security scanning endpoint. Pass in a JSON plan as specified
above, with one or both of the `--html_out` and `--json_out` parameters. This
will generate HTML and/or JSON output and save it to the specified files or
files.

The script is currently configured to never fail; you will have to change the
failure conditions at the bottom of the script to start breaking the build on
the basis of these results. We recommend that, when you first deploy IaC, you
begin by always passing. This gives you time to use the results to familiarize
yourself with how scanning works against your Terraform codebase, confirm the
results align with your expectations, and to educate your DevOps teams on how
to read and address any failures. After collaborative evaluation of the
results, DevOps users will be better prepared to address issues independently.
"""


import sys
import json
import requests
from datetime import datetime, timedelta
import argparse
import logging
import os


parser = argparse.ArgumentParser()
parser.add_argument('divvy_url')
parser.add_argument('config_name')
parser.add_argument('terraform_json')
parser.add_argument('--debug', action='store_true', default=False, help='dump JSON output')
parser.add_argument('--scan_name', default='API Scan', help='Name for the job that will appear in DivvyCloud.')
parser.add_argument('--author', default='API Author', help='Author of the job that will appear in DivvyCloud.')
parser.add_argument('--html_out', default=None, help='Takes a filename. If specified, download an HTML report to the specified file.')
parser.add_argument('--json_out', default=None, help='Takes a filename. If specified, download a JSON report to the specified file.')
parser.add_argument('--auth_for_submission', action='store_true', default=False,
                    help=("If you've configured IaC to require authentication for scan submission, "
                          "set this flag to authenticate for that submission."))


# API Key to authenticate against the API
api_key = os.environ.get('DIVVY_API_KEY')

def scan_template(base_url, scan_mode, scan_filename, api_key=None):
    """
    Use Divvy's `/scan` API to submit a JSON-formatted Terraform plan.
    """

    # Prepare Accept headers and URL parameters to requrest JSON or HTML
    # response
    params = {}
    if scan_mode == 'json':
        accept_value = 'application/json'
        params['readable'] = 'true'
    elif scan_mode == 'html':
        accept_value = 'text/html'
    else:
        raise ValueError('Invalid value {} for scan_mode'.format(scan_mode))

    with open(args.terraform_json) as plan_json_file:
        tf_template_str = json.load(plan_json_file)
    data = {
        'scan_name': scan_name,
        'author_name': author,
        'scan_template': json.dumps(tf_template_str),
        'config_name': config_name,
        'iac_provider': 'terraform'
    }

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': accept_value,
    }
    if api_key:
        headers['Api-Key'] = api_key

    response = requests.post(
        url=base_url + '/v3/iac/scan',
        headers=headers,
        data=json.dumps(data),
        params=params
    )

    with open(scan_filename, 'w') as f:
        f.write(response.text)

    return response

if __name__ == '__main__':

    args = parser.parse_args()

    html_out = args.html_out
    json_out = args.json_out
    two_phases = (html_out and json_out)
    if two_phases or json_out:
        scan_mode = 'json'
        scan_filename = json_out
    elif html_out:
        scan_mode = 'html'
        scan_filename = html_out
    else:
        raise ValueError('Must specify at least one of `--html_out <filename>` '
                         'and/or `--json_out <filename>`')

    config_name = args.config_name
    scan_name = args.scan_name
    author = args.author
    base_url = args.divvy_url

    # If `/scan` requires authentication (`--auth_for_submission`), or if we
    # will be getting both JSON and HTML reports and thus need to hit the
    # authenticated `/scans/id` API, get a session token.
    if two_phases and not api_key:
        raise ValueError("Authentication is required for this action, but "
                            "you didn't provide an API Key DIVVY_API_KEY.")

    result = scan_template(
        base_url=base_url,
        scan_mode=scan_mode,
        scan_filename=scan_filename,
        api_key=api_key  # May be `None`
    )
    status_code = result.status_code

    if two_phases:
        # Hit the `get_scans` endpoint to get the HTML report. This endpoint is
        # always authenticated so it requires a session token non-optionally.
        response = requests.get(
            url=base_url + '/v3/iac/scans/{}'.format(
                json.loads(result.text)['build_id']
            ),
            headers={
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'text/html',
                'Api-Key': api_key
            }
        )
        with open(html_out, 'w') as f:
            f.write(response.text)


    # Fail based on the API results from the `/scan` request. Customize this to
    # your use case.
    if status_code == 200:
        message = "[DivvyCloud]: Scan completed successfully.  All insights have passed."
        exit_code = 0
    elif status_code == 202:
        message = "[DivvyCloud]: Scan completed successfully, but with warnings.  All failure-inducing insights have passed, but some warning-inducing insights did not."
        exit_code = 0  # Change to a nonzero positive integer to fail the build
    elif status_code == 406:
        message = "[DivvyCloud]: Scan completed, but one or more insights have failed.  Please check the DivvyCloud console for more information."
        exit_code = 0  # Change to a nonzero positive integer to fail the build
    else:
        message = "[DivvyCloud]: IaC Endpoint Request returned HTTP Error {}".format(status_code)
        exit_code = 0  # Change to a nonzero positive integer to fail the build

    print(message)
    sys.exit(exit_code)