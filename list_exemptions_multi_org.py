# Script to list all organizations in DivvyCloudf

import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

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

# Get Exemption info

# Get Org info
def get_orgs():
    data = {}
    response = requests.get(
        url=base_url + '/v2/prototype/domain/organizations/detail/get',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    

def switch_org(name):
    data = {"organization_name": name }
    response = requests.post(
        url=base_url + '/v2/prototype/domain/switch_organization',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response

def get_exemptions():
    data = {"search":"","pack":None,"badges":[],"badge_filter_operator":"OR"}
    response = requests.post(
        url=base_url + '/v2/public/exemptions/list?page=1&page_size=2000',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    

# List all orgs and get the org names
org_list = get_orgs()['organizations']

print("List of organizations we're printing exemptions for: ")
for org in org_list:
    print(org['name'])

print("===================================")

for org in org_list:
    name = org['name']
    print("Switching to org " + name)
    switch_org(name)

    print("Exemptions for org " + name + ":")
    print(get_exemptions())

    print ("\n")
    print("===================================")

