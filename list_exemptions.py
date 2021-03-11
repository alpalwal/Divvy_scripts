# Script to list all organizations in DivvyCloudf

import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

# Username/password to authenticate against the API
username = ""
password = "T" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URL
base_url = ""

# Param validation
if not username:
    username = input("Username: ")

if not password:
    passwd = getpass.getpass('Password:')
else:
    passwd = password

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

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

# Get Org info
def get_exemptions():
    data = {"search":"","pack":None,"badges":[],"badge_filter_operator":"OR"}
    response = requests.post(
        url=base_url + '/v2/public/exemptions/list?page=1&page_size=2000',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    

# Create the pack
exemption_info = get_exemptions()
print(exemption_info)

