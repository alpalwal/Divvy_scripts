# Build list of all insights / actions / bots
import csv
import json
from botocore.vendored import requests
import boto3
from collections import defaultdict
import os
from base64 import b64decode

def lambda_handler(event, context):

    bucket_name = os.environ['BUCKET_NAME']

    ENCRYPTED = os.environ['PASSWORD']
    # Decrypt code should run once and variables stored outside of the function
    # handler so that these are decrypted once per container
    password = boto3.client('kms').decrypt(
        CiphertextBlob=b64decode(ENCRYPTED),
        EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
    )['Plaintext'].decode('utf-8')
    
    base_url = os.environ['DIVVY_URL']
    login_url = base_url + '/v2/public/user/login'
    
    username = os.environ['USERNAME']

    # Shorthand helper function
    def get_auth_token():
        response = requests.post(
            url=login_url,
            data=json.dumps({"username": username, "password": password}),
            headers={
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json'
            })
        return response.json()['session_id']
    auth_token = get_auth_token()

    def get_info(url):
        response = requests.get(
            url=base_url + url,
            headers={
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json',
                'X-Auth-Token': auth_token
            }
        )
        return response.json()

    # Get the version of the current divvy instance 
    def get_version():
        response = requests.get(
            url=base_url + '/client_version',
            data={},
            headers={
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json',
                'X-Auth-Token': auth_token
                }
            )
        return response.json()    

    version = get_version() 

    # Filenames
    insights_filename = 'divvy_insights_' + version + '.csv'
    filters_filename = 'divvy_filters_' + version + '.csv'
    bots_filename = 'divvy_bots_' + version + '.csv'

    insights_path = '/tmp/' + insights_filename
    filters_path = '/tmp/' + filters_filename
    bots_path = '/tmp/' + bots_filename


    # Build insights CSV
    with open(insights_path, 'w') as insightsfile:
        headers = ['Name', 'Description', 'Default Severity (5 is high)', 'Updated At', 'AWS', 'AZURE', 'GCP', 'ALICLOUD', 'K8S', 'OCI']
        writer = csv.writer(insightsfile)
        packs = get_info('/v2/public/insights/packs/list')
        pack_ids = []
        pack_descriptions = defaultdict(dict)
        for pack in packs:
            if pack['source'] != 'backoffice':
                continue
            headers.append(pack['name'])
            pack_ids.append(pack['pack_id'])

        writer.writerow(headers)
        for pack in packs:
            if pack['source'] != 'backoffice':
                continue

        for insight in get_info('/v2/public/insights/list'):
            if insight['source'] == 'custom':
                continue

            clouds = insight['supported_clouds'] if insight['supported_clouds'] else []
            aws = 'Y' if 'AWS' in clouds else 'N'
            azure = 'Y' if 'AZURE_ARM' in clouds else 'N'
            gcp = 'Y' if 'GCE' in clouds else 'N'
            alicloud = 'Y' if 'ALICLOUD' in clouds else 'N'
            k8s = 'Y' if 'K8S' in clouds else 'N'
            oci = 'Y' if 'OCI' in clouds else 'N'
            cells = [insight['name'], insight['description'], insight['severity'], insight['updated_at'], aws, azure ,gcp, alicloud, k8s, oci]
            for pack_id in pack_ids:
                compliance_rule = ''
                for pack in packs:
                    if pack['pack_id'] == pack_id:
                            for item in pack.get('backoffice_metadata', []):
                                if item['pack_id'] == pack_id and item['template_id'] == insight['insight_id']:
                                    if item['description']:
                                        compliance_rule = item['description'].encode('utf-8')
                cells.append(compliance_rule)
            writer.writerow(cells)
    insightsfile.close()


    # Get filter and bots list (one endpoint for both)
    filters_and_bots_data = get_info('/v2/public/botfactory/function-registry/list')

    # Make filter spreadsheet
    with open(filters_path, 'w') as filtersfile:
        headers = ['Name', 'Supported Resources', 'Version', 'Description', 'AWS', 'AZURE', 'GCP', 'ALICLOUD', 'K8S', 'OCI']
        writer = csv.writer(filtersfile)
        writer.writerow(headers)

        filter_list = filters_and_bots_data['filters']
        for row in filter_list:
            clouds = row['supported_clouds'] if row['supported_clouds'] else []
            aws = 'Y' if 'AWS' in clouds else 'N'
            azure = 'Y' if 'AZURE_ARM' in clouds else 'N'
            gcp = 'Y' if 'GCE' in clouds else 'N'
            alicloud = 'Y' if 'ALICLOUD' in clouds else 'N'
            k8s = 'Y' if 'K8S' in clouds else 'N'
            oci = 'Y' if 'OCI' in clouds else 'N'

            if aws == 'N' and azure == 'N' and gcp == 'N' and alicloud == 'N' and k8s == 'N' and oci == 'N':
                aws = azure = gcp = alicloud = k8s = oci = 'Y' 

            if row['name'] == 'Instance Without Recent Snapshot (VMware Only)' or row['name'] == 'Instance VMware Tools Status':
                continue

            cells = [row['name'], str(row['supported_resources']), row['version'], row['description'], aws, azure, gcp, alicloud, k8s, oci]
            writer.writerow(cells)
    filtersfile.close()


    # Make bots spreadsheet
    with open(bots_path, 'w') as botsfile:
        headers = ['Name', 'Supported Resources', 'Description', 'AWS', 'AZURE', 'GCP', 'ALICLOUD', 'K8S', 'OCI', 'Permissions']
        writer = csv.writer(botsfile)
        writer.writerow(headers)

        bots_list = filters_and_bots_data['actions']
        for row in bots_list:
            clouds = row['supported_clouds'] if row['supported_clouds'] else []
            aws = 'Y' if 'AWS' in clouds else 'N'
            azure = 'Y' if 'AZURE_ARM' in clouds else 'N'
            gcp = 'Y' if 'GCE' in clouds else 'N'
            alicloud = 'Y' if 'ALICLOUD' in clouds else 'N'
            k8s = 'Y' if 'K8S' in clouds else 'N'
            oci = 'Y' if 'OCI' in clouds else 'N'

            if aws == 'N' and azure == 'N' and gcp == 'N' and alicloud == 'N' and k8s == 'N':
                aws = azure = gcp = alicloud = k8s = 'Y' 

            cells = [row['name'], str(row['supported_resources']), row['description'], aws, azure, gcp, alicloud, k8s, oci, row['permissions']]
            writer.writerow(cells)
    botsfile.close()


    ## Send The CSVs to S3
    client = boto3.client('s3')

    try:
        print(client.upload_file(insights_path, bucket_name, insights_filename))
        print(client.upload_file(filters_path, bucket_name, filters_filename))
        print(client.upload_file(bots_path, bucket_name, bots_filename))
    except Exception as e:
        print(e)
    