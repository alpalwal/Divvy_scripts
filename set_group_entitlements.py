import json
import requests
import getpass

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

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'Api-Key': key
}

# set entitlements 
def set_entitlements():
    data = {
            "group_ids": [
                
                ],
            "entitlements": [
                    {
                        "namespace": "botfactory",
                        "role": "viewer"
                    },
                    {
                        "namespace": "collections",
                        "role": "viewer"
                    },
                    {
                        "namespace": "events",
                        "role": "viewer"
                    },
                    {
                        "namespace": "exemptions",
                        "role": "viewer"
                    },
                    {
                        "namespace": "groups",
                        "role": "viewer"
                    },
                    {
                        "namespace": "iac",
                        "role": "viewer"
                    },
                    {
                        "namespace": "iam",
                        "role": "viewer"
                    },
                    {
                        "namespace": "insights",
                        "role": "admin"
                    },
                    {
                        "namespace": "tags",
                        "role": "viewer"
                    }
                    ]
                }

    response = requests.post(
        url=base_url + '/v2/public/entitlements/set',
        data=json.dumps(data),
        headers=headers
    )
    return response.json

print(set_entitlements())