#Script to delete users from DivvyCloud

import json
import requests
import getpass
import csv

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise


# User ID to delete
user_id = ""

# User API Key (generate in the profile section of the Divvy UI)
api_key = ""

# API URL
base_url = ""

# Param validation
if not api_key:
    key = getpass.getpass('API Key:')
else:
    key = api_key

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

if not user_id:
    user_id = input("User ID: ")

# Full URL
login_url = base_url + '/v2/public/user/login'

# Full URL
login_url = base_url + '/v2/public/user/login'

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'Api-Key': key
}

# Delete user function
def delete_users():
    data = {}
    response = requests.delete(
        url=base_url + '/v2/prototype/user/divvyuser:'+ user_id + ':/delete',
        verify=False,
        data=json.dumps(data),
        headers=headers
    )
    try:
        return response.json()
    except:
        return response 

delete_users()

print("Deleting User: " + user_id)