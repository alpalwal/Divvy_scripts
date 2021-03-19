# Script to bulk add users into divvy

import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

# Key 
api_key = ""

# API URL
base_url = ""

users_to_add = [
    {"name": "Bob Bobinson",
        "email": "bbobinson@rapid9.com",
        "username": "bbobinson"},
    {"name": "Bob Bobinson",
        "email": "bbobinson@rapid9.com",
        "username": "bbobinson"}
]

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
def create_user(user):
    data = {
        "authentication_type": "saml",
        "group_ids": [],
        "access_level": "ORGANIZATION_ADMIN",
        "authentication_server_id": 3,
        "username": user["username"],
        "name": user["name"],
        "email": user['email']
    }
    response = requests.post(
        url=base_url + '/v2/public/user/create',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    


for user in users_to_add:
    try:
        new_user_info = create_user(user)
        print("User created: %s" % new_user_info['username'])

    except Exception as e:
        print(user)
        print(e)

