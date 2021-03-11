import json
import requests
import getpass
import re

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

# For each account you want to add, add a new block in aws_accounts
aws_accounts = [
    {
        "account_name": "Production Acct",
        "account_number": 12345,
        "role_arn": "arn:aws:iam::12435678:role/DivvyCloudCrossAcctRole-Role-SOJ9J0W1B0SO",
        "external_id": "divvycloud"
    },
    {
        "account_name": "KB-testtt",
        "account_number": 12345654,
        "role_arn": "arn:aws:iam::12345654:role/DivvyCloudCrossAcctRole-Role-SOJ9J0W1B0SO",
        "external_id": "divvycloud"
    }
]

#### Prefix > org mapping:
alias_org_mapping = [
    {"alias":"KB",
    "org":"KBorg"
    },
    {"alias":"GP",
    "org":"GPorg"
    },
    {"alias":"bobacct",
    "org":"boborg"
    }
]

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

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

# Switch to the org to add the account in
def switch_org(name):
    data = {"organization_name": name }
    response = requests.post(
        url=base_url + '/v2/prototype/domain/switch_organization',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response

org_list = get_orgs()['organizations']

print("========= List of organizations we can add accounts to: =========")
for org in org_list:
    print(org['name'])

print("\n\n=========================================")

# Onboard the accounts
print("Onboarding AWS accounts into DivvyCloud")
print("=========================================")

skipped_accounts = []
added_accounts = []

for account in aws_accounts:
    account_name = account['account_name']
    account_number = int(account['account_number'])
    role_arn = account['role_arn']
    external_id = account['external_id']    

    print("\nWorking on account: " + account_name)

    ## pull the account name and strip everything pre-hyphen
    regex = r"(^[A-Za-z]+)-"
    match = re.findall(regex,account_name)
    
    if match:
        print("Found an account name prefix to match. Looking for the corresponding org")
        org_prefix = match[0]
    else:
        print("Couldn't find an alias prefix to match to an org. Saving for later parsing.")
        skipped_accounts.append(account)
        continue

    for mapping in alias_org_mapping:
        if mapping['alias'] == org_prefix:
            print("Switching org to " + mapping['org'] + " and adding account: " + account_name)
            # switch org
            switch_org(mapping['org'])

            # Add account
            try:    
                onboard_output = onboard_aws(account_name,account_number,role_arn,external_id)
            except Exception as e:
                print ("An error occurred. " + str(e))

            try:
                if onboard_output['status']:
                    onboard_status = "Success"
            except KeyError:    
                if onboard_output['error_message']:
                    onboard_status = "Error"

            added_accounts.append("Org: " + mapping['org'] + " Account Name: " + account_name + "| Status: " + onboard_status + " | Account Number: " + str(account_number))
            break

print("\n=========================================")
print("Accounts that were attempted to be added:")
for account in added_accounts:
    print(account)

print("\n===============================")
print("Accounts that weren't added:")
for account in skipped_accounts:
    print(account)