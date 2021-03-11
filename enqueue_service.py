# Script to enqueue a specific job in Divvy
# usage: enqueue_service.py <accountID> <region_name> <job_name>


import json
import requests
import getpass
import sys

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

try:
    cloud_account_id = str(sys.argv[1])
    region_name = str(sys.argv[2])
    job_name = str(sys.argv[3])
except:
    print("Not all required inputs were found. Usage: enqueue_service.py <accountID> <region_name> <job_name>")
    exit()

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

# Get Acct info
def get_account_list():
    data = {
        "filters": [],
        "limit": 500,
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

# Get last harvest info info
def get_harvest_info(org_id):
    data = {}

    response = requests.get(
        url=base_url + '/v2/public/divvy/cloud/divvyorganizationservice:' + str(org_id) + '/last_harvest/get',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()       

# enqueue job
def enqueue_job(job_to_queue):
    data = job_to_queue

    response = requests.post(
        url=base_url + '/v2/public/divvy/cloud/enqueue_harvest_job',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response       

# Parse through the info to pretty print the accounts
account_list = get_account_list()

for cloud in account_list['clouds']:
    try:
        if cloud['account_id'] == cloud_account_id:
            org_id = cloud['id']
    except KeyError as e: ## K8s clusters don't have account_ids and so it'll key error out
        continue

try:
    org_id
except NameError:
    print("Could not find a matching cloud account ID for account " + cloud_account_id + ". Please check the inputs and try again.")    
    exit()

last_harvest_info = get_harvest_info(org_id)

for harvest in last_harvest_info:
    if harvest['region'] == region_name:
        job = harvest['schedule']['job']
        split_job = job.split(':')[1]

        if split_job == job_name:
            job_to_queue = harvest['schedule']

try:
    job_to_queue
except NameError:
    print("Could not find a matching job in this region. Please check the inputs and try again.")    
    exit()

response = enqueue_job(job_to_queue)

if response.status_code == 200:
    print ('Job successfully enqueued')
else:
    print ('Unknown error occured. Exiting. Status code: ' + str(response.status_code))


