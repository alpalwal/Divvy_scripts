#Script to delete users from DivvyCloud

import json
import requests
import getpass
import csv

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise


# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 
user_id = ""

# API URL
base_url = "https://sales-demo.divvycloud.com"

# Param validation
if not username:
    username = input("Username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

if not user_id:
    user_id = input("User ID: ")

# Full URL
login_url = base_url + '/v2/public/user/login'

# Shorthand helper function
def get_auth_token():
    response = requests.post(
            url=login_url,
        verify=False,
        data=json.dumps({"username": username, "password": passwd}),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        })
    return response.json()['session_id']

auth_token = get_auth_token()

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'X-Auth-Token': auth_token
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