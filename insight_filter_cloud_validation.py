# Build list of all insights / actions / bots
import csv
import io
import json
import requests
import getpass
from collections import defaultdict

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

# User API Key (generate in the profile section of the Divvy UI)
api_key = ""

# API URL
base_url = ""

# # Param validation
if not api_key:
    key = getpass.getpass('API Key:')
else:
    key = api_key

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

if not version:
    version = input("Version with underscores - ex. 20_1_1: ")

# API URLs
base_url = 'https://sales-demo.divvycloud.com'

login_url = base_url + '/v2/public/user/login'

# Filenames
insights_filename = 'divvy_insights_' + version + '.csv'
filters_filename = 'divvy_filters_' + version + '.csv'
bots_filename = 'divvy_bots_' + version + '.csv'

# Endpoints
packs_url = '/v2/public/insights/packs/list'
filters_and_bots_url = '/v2/public/botfactory/function-registry/list'
insights_url = '/v2/public/insights/list'

# Full URL
login_url = base_url + '/v2/public/user/login'

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'Api-Key': key
}

def get_info(url):
    response = requests.get(
        url=base_url + url,
        verify=False,
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-Auth-Token': auth_token
        }
    )
    return response.json()

# # Build insights CSV
with open(insights_filename, 'w') as csvfile:
    headers = ['Name', 'Description', 'AWS', 'AZURE', 'GCP', 'ALICLOUD']
    writer = csv.writer(csvfile)
    packs = get_info(packs_url)
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

    for insight in get_info(insights_url):
        if insight['source'] == 'custom':
            continue
        clouds = insight['supported_clouds'] if insight['supported_clouds'] else []
        aws = 'Y' if 'AWS' in clouds else 'N'
        azure = 'Y' if 'AZURE_ARM' in clouds else 'N'
        gcp = 'Y' if 'GCE' in clouds else 'N'
        alicloud = 'Y' if 'ALICLOUD' in clouds else 'N'
        cells = [insight['name'], insight['description'], aws, azure ,gcp, alicloud]
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


# Get filter and bots list (one endpoint for both)
filters_and_bots_data = get_info(filters_and_bots_url)

# Make filter spreadsheet
with open(filters_filename, 'w') as outfile:
    headers = ['Name', 'Supported Resources', 'Description', 'AWS', 'AZURE', 'GCP', 'ALICLOUD', 'K8S']
    writer = csv.writer(outfile)
    writer.writerow(headers)

    filter_list = filters_and_bots_data['filters']
    for row in filter_list:
        clouds = row['supported_clouds'] if row['supported_clouds'] else []
        aws = 'Y' if 'AWS' in clouds else 'N'
        azure = 'Y' if 'AZURE_ARM' in clouds else 'N'
        gcp = 'Y' if 'GCE' in clouds else 'N'
        alicloud = 'Y' if 'ALICLOUD' in clouds else 'N'
        k8s = 'Y' if 'K8S' in clouds else 'N'

        if aws == 'N' and azure == 'N' and gcp == 'N' and alicloud == 'N' and k8s == 'N':
            aws = azure = gcp = alicloud = k8s = 'Y' 

        cells = [row['name'], str(row['supported_resources']), row['description'], aws, azure, gcp, alicloud, k8s]
        writer.writerow(cells)
outfile.close()


# Make bots spreadsheet
with open(bots_filename, 'w') as outfile:
    headers = ['Name', 'Supported Resources', 'Description', 'AWS', 'AZURE', 'GCP', 'ALICLOUD', 'K8S', 'Permissions']
    writer = csv.writer(outfile)
    writer.writerow(headers)

    bots_list = filters_and_bots_data['actions']
    for row in bots_list:
        clouds = row['supported_clouds'] if row['supported_clouds'] else []
        aws = 'Y' if 'AWS' in clouds else 'N'
        azure = 'Y' if 'AZURE_ARM' in clouds else 'N'
        gcp = 'Y' if 'GCE' in clouds else 'N'
        alicloud = 'Y' if 'ALICLOUD' in clouds else 'N'
        k8s = 'Y' if 'K8S' in clouds else 'N'

        if aws == 'N' and azure == 'N' and gcp == 'N' and alicloud == 'N' and k8s == 'N':
            aws = azure = gcp = alicloud = k8s = 'Y' 

        cells = [row['name'], str(row['supported_resources']), row['description'], aws, azure, gcp, alicloud, k8s, row['permissions']]
        writer.writerow(cells)
outfile.close()