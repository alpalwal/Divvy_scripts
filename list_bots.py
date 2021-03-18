# Script to list all organizations in DivvyCloudf

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
def get_org():
    data = {"filters":[],"limit":50,"offset":0}

    response = requests.post(
        url=base_url + '/v2/public/botfactory/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()

# Create the pack
org_info = get_org()
print(org_info)

