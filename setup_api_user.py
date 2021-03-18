# Script to generate an API key for a user
# https://docs.divvycloud.com/docs/user-roles
# https://docs.divvycloud.com/reference#divvycloud-api-keys

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

# Find your user ID
def list_user_ids():
    data =  {}

    # 2x calls - one for normal users, one for admins
    org_users_response = requests.get(
        url=base_url + '/v2/public/users/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )   
        
    # 2x calls - one for normal users, one for admins
    domain_users_response = requests.post(
        url=base_url + '/v2/prototype/domains/admins/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    
    # Merge the 2 user lists since they have basically the same structure
    all_users = org_users_response.json()['users'] + domain_users_response.json()['users']
    
    return all_users

# Create the API key from the authenticated user
def create_key(user_id):
    data =  {
        "user_id":user_id,
        "key_length":32
    }
    response = requests.post(
        url=base_url + '/v2/public/apikey/create',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    


# List all users
user_ids = list_user_ids()

# Match your username to your ID in the user_ids list
for user in user_ids:   
    if username == user['username']:
        user_id = user['resource_id'].split(":")[1]

if not user_id:
    print("Couldn't find user ID. Exiting")
    exit()

# Call the create function and print the key
print(create_key(str(user_id)))


