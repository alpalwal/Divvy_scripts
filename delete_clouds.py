# Delete duplicate AWWS projects

import json
import requests
import getpass

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

# Full URL
login_url = base_url + '/v2/public/user/login'

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'Api-Key': key
}

# Get Org info
def get_clouds():
    data = {}

    response = requests.post(
        url=base_url + '/v2/public/clouds/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    

# Get Org info
def remove_account(account_id):
    data = {}
    response = requests.post(
        url=base_url + '/v2/public/cloud/' + account_id + '/delete',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response #.json()        

# list clouds and look for gcp
while True:
    clouds_list = get_clouds()
    if len(clouds_list['clouds']) > 0:
        for cloud in  clouds_list['clouds']: 
            if cloud['cloud_type_id'] == 'GCE':
                if "sys-" in cloud['account_id']:
                    print(cloud)
                    account_id = cloud['group_resource_id']
                    remove_account(account_id)
    else:
        print("All bad projects removed!")
        break




