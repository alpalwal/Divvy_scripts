'''
Script to onboard multiple AWS accounts via cross account role
Sample onboard_output

[Alex-MBP scripts]$python onboard_aws_bulk_roles.py 
Onboarding AWS accounts into DivvyCloud
Account Name: POCs| Status: Success | Account Number: 625820357955
Account Name: test| Status: Error | Account Number: 625820357958
'''

import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

# For each account you want to add, add a new block in aws_accounts
aws_accounts = [
    {
        "account_name": "Production Acct",
        "account_number": 62512450955,
        "role_arn": "arn:aws:iam::23456:role/DivvyCloudCrossAcctRole-Role-SOJ9J0W1B0SO",
        "external_id": "divvycloud"
    },
    {
        "account_name": "Dev Acct",
        "account_number": 12345654,
        "role_arn": "arn:aws:iam::12345654:role/DivvyCloudCrossAcctRole-Role-SOJ9J0W1B0SO",
        "external_id": "divvycloud"
    }
]

# User API Key (generate in the profile section of the Divvy UI)
divvy_api_key = ""

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
def onboard_aws(account_name,account_number,role_arn,external_id):
    data = {
        "creation_params": 
        {
            "cloud_type":"AWS",
            "authentication_type":"instance_assume_role",
            "name": account_name,
            "account_number":account_number,
            "role_arn":role_arn,
            "duration":3600,
                "external_id": external_id,
            "session_name":"DivvyCloud"
        }
    }
    response = requests.post(
        url=base_url + '/v2/prototype/cloud/add',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    

# Onboard the accounts
print("Onboarding AWS accounts into DivvyCloud")

for account in aws_accounts:
    account_name = account['account_name']
    account_number = int(account['account_number'])
    role_arn = account['role_arn']
    external_id = account['external_id']

    try:    
        onboard_output = onboard_aws(account_name,account_number,role_arn,external_id)
    except Exception as e:
        print ("An error occurred")

    try:
        if onboard_output['status']:
            onboard_status = "Success"
    except KeyError:    
        if onboard_output['error_message']:
            onboard_status = "Error"

    print("Account Name: " + account_name + "| Status: " + onboard_status + " | Account Number: " + str(account_number))

