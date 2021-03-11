#Create compliance scorecard report
import json
import requests
import getpass
import csv

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

### SUBSCRIPTION PARAMETERS
subscription_email_hour = 0
subscription_email_minute = 12
subscription_name = "troubleshooting6-5-20v1"
subscription_schedule = "daily"
subscription_day_of_week = "monday"
subscription_emails = ['alex_corstorphine@rapid7.com']
subscription_email_title = "Divvy Report"
resource_tags = []

# Add another line for each badge that you want to scope on (currently set to look for both badges, not either badge)
config_badges = [
    ["env","development"],
    ["custom","123"]
]

### ONLY can be one of these and the other needs to be None
backoffice_pack_id = 23
custom_pack_id = None 

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

## 3 calls need to be made. Create an export, configure the export and link it to the created export, and then create a subscription that's linked to the export
def create_export():
    data = {"name": subscription_name + " export"}

    response = requests.post(
        url=base_url + '/v2/compliance/score-card/export-upload',
        verify=False,
        data=json.dumps(data),
        headers=headers
        )
    try:
        return response.json()
    except:
        return response   


def create_export_config(export_id):
    data = {
        "custom_pack_id": custom_pack_id,
        "backoffice_pack_id": backoffice_pack_id,
        "organization_service_filters": {
            "organization_service_ids": [],
            "cloud_types": [],
            "badges": config_badges,
          },
        "insight_filters": {
            "severity": [],
            "insight_ids": [],
            "resource_types": []
            },
        "bad_only": False,
        "export_id": export_id,
        "name": subscription_name + " export config",
        "resource_tags": []
    }

    response = requests.post(
        url=base_url + '/v2/compliance/score-card/export-upload/configs',
        verify=False,
        data=json.dumps(data),
        headers=headers
        )
    try:
        return response.json()
    except:
        return response           

def create_subscription(item_id):
    data = {
        "minute": subscription_email_minute,
        "hour": subscription_email_hour,
        "name": subscription_name,
        "schedule": subscription_schedule,
        "day_of_week": subscription_day_of_week,
        "email_addresses": subscription_emails,
        "email_sub_title": subscription_email_title,
        "resource_tags": resource_tags,
        "badges": [],
        "badge_filter_operator": "AND",
        "item_type": "scorecard",        
        "item_id": item_id
    }

    response = requests.post(
        url=base_url + '/v2/subscriptions/',
        verify=False,
        data=json.dumps(data),
        headers=headers
        )
    try:
        return response.json()
    except:
        return response   

##### Do work
export_id = create_export()['id']
print("Creating export")
print("EXPORT ID " + str(export_id))

print("Linking export to a config")
print(create_export_config(export_id))

print("Creating subscription that's linked to the export config")
print(create_subscription(export_id))


## SAMPLE calls and inputs/response

'''
https://sales-demo.divvycloud.com/v2/compliance/score-card/export-upload
{name: "alex export"}
{"id": 43}

https://sales-demo.divvycloud.com/v2/compliance/score-card/export-upload/configs
{
  "custom_pack_id": null,
  "backoffice_pack_id": 3,
  "organization_service_filters": {
    "organization_service_ids": [],
    "cloud_types": [],
    "badges": [
      [
        "Compliance",
        "SOC2"
      ]
    ]
  },
  "insight_filters": {
    "severity": [],
    "insight_ids": [],
    "resource_types": []
  },
  "bad_only": false,
  "export_id": 43,
  "name": "alex export config",
  "resource_tags": []
}

https://sales-demo.divvycloud.com/v2/subscriptions/
{
  "minute": 0,
  "hour": 0,
  "name": "alex",
  "schedule": "daily",
  "day_of_week": "monday",
  "email_addresses": [
    "alex_corstorphine@rapid7.com"
  ],
  "email_sub_title": "test",
  "resource_tags": [],
  "badges": [],
  "badge_filter_operator": "OR",
  "item_type": "scorecard",
  "item_id": 43
}

Response: {"id": 58}
'''