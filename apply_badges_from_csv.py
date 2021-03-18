# Script to list all organizations in DivvyCloudf

import json
import requests
import getpass
import json
import sys

requests.packages.urllib3.disable_warnings() # throws SSL warnings otherwise

# User API Key (generate in the profile section of the Divvy UI)
api_key = ""

# API URL
base_url = ""

try:
    file_name = str(sys.argv[1])
except:
    print("No file name input. Exiting. Usage: python apply_badges_from_csv.py <file name>")
    exit()

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


# Get Acct info so we can map account IDs to org IDs
def get_account_list():
    data = {
        "filters": [],
        "limit": 5000,
        "offset": 0,
        "order_by": "name"
    }

    response = requests.get(
        url=base_url + '/v2/public/clouds/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()   


# list out current acct badges
def get_badges(account_org_id):
    data = {}
    response = requests.post(
        url=base_url + '/v2/public/badges/divvyorganizationservice:' + account_org_id + '/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    

# Send up new list of badges
def add_badges(account_org_id,badges):
    data = {
        "target_resource_ids": [
            "divvyorganizationservice:" + account_org_id
        ],
        "badges": badges        
    }

    response = requests.post(
        url=base_url + '/v2/public/badges/divvyorganizationservice:' + account_org_id + '/update',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response   

# Get Acct info so we can map account IDs to org IDs
account_list = get_account_list()


with open(file_name) as f:
    badge_data = json.load(f)


for account_to_badge in badge_data:
    print("")
    print("==== Trying to badge account " + account_to_badge['account_id'])
    # Get org ID from acct ID
    for cloud_account in account_list['clouds']:
        try:
            if cloud_account['account_id'] == account_to_badge['account_id']:
                account_org_id = str(cloud_account['id'])
                print("Found Org ID: " + account_org_id)
        except Exception:
            pass # K8s clusters don't have account IDs. We'll skip these

    try:
       account_org_id
    except NameError:
        print("Couldn't find an org ID for account " + account_to_badge['account_id'] + ". Skipping")
        continue

    # List out current badges on the account
    badge_info = get_badges(account_org_id)
    
    # Add new badges into the existing badges <<<<<< ADD VALIDATION FOR DUPES- it'll 400 otherwise
    for badge in account_to_badge['badges']:
        badge_info.append(badge)

    badging_result = add_badges(account_org_id,badge_info)

    if badging_result.status_code == 400:
        print("Updating badges failed. Most likely because there was a duplicate key in the JSON. Skipping")
        continue
    elif badging_result.status_code == 204:
        print("Account successfully badged.")