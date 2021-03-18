# Script to onboard an AWS account into divvycloud via key/secret

import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

# User API Key (generate in the profile section of the Divvy UI)
divvy_api_key = ""

# Info about the cloud you're onboarding. If you don't put in the secret, you'll be prompted for it and it'll be hidden
api_key = ""
api_secret = ""
if not api_secret:
    api_secret = getpass.getpass('API Secret:')

account_name = "" # Whatever you call this account (Alex-sandbox, divvy-prod, etc.)
account_number = ""


# API URL
base_url = ""

# # Param validation
if not divvy_api_key:
    key = getpass.getpass('API Key:')
else:
    key = divvy_api_key

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
def onboard_aws(account_name,account_number,api_key,api_secret):
    data = {
        "creation_params": {		
            "cloud_type":"AWS",
            "authentication_type":"standard",
            "name":account_name,
            "account_number":account_number,
            "api_key":api_key,
            "secret_key":api_secret
        }
    }
    response = requests.post(
        url=base_url + '/v2/prototype/cloud/add',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    

# Create the pack
print("Onboarding AWS account into DivvyCloud via API key/secret")
onboard_output = onboard_aws(account_name,int(account_number),api_key,api_secret)
print(onboard_output)
# Successful output:
# {'status': 'REFRESH', 'group_resource_id': 'divvyorganizationservice:1', 'name': 'test', 'resource_id': 'divvyorganizationservice:1', 'cloud_type_id': 'AWS', 'creation_time': '2019-07-11 02:40:51.443796', 'id': 1}
