#Bot history

import json
import requests
import getpass
import csv

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

#Add json for data
def get_bot_history():
    data = {
            "filters": [
                {"field_name":"organization_service_id","filter_type":"EXACT","filter_value":"1"}
            ],
        "limit":500,
        "offset":0,
        "order_by":"start_time DESC"
    }
    
    response = requests.post(
            url=base_url + '/v2/prototype/scheduled_events/history/list',
        verify=False,
        data=json.dumps(data),
        headers=headers
        )
    try:
        return response.json()
    except:
        return response

#List Events
bot_history = get_bot_history()
event_list = []
event_list.extend(bot_history['events'])

#print(list_bot_history)

with open('bot_history_5_1.csv', mode='w', newline="") as csv_file:
    fieldnames = ['bot_name','resource_type','name','provider_id','last_run_status','target_resource_id','event_type','start_time','finish_time']
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)
    for events in event_list:
        writer.writerow([events['bot_name'],events['resource_type'],events['name'],events['provider_id'],events['last_run_status'],events['target_resource_id'],events['event_type'],str(events['start_time']),str(events['finish_time'])])