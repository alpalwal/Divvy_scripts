'''
- Generally use the list_organizations_api_user.py as a starting template
- go to divvy - right click > inspect > network (in chrome)
- do whatever it is you're trying to automate
- in the network calls, look for the one that does the action you're looking for
- Grab - URL / Method / Parameters / Response

Request URL: https://sales-demo.divvycloud.com/v2/public/clouds/status/set
Request Method: POST
Payload (view source to get it in JSON) - {"resource_ids":["divvyorganizationservice:544"],"status":"PAUSED"}
{
  "resource_ids": [
    "divvyorganizationservice:544"
  ],
  "status": "PAUSED" ## Other status is "DEFAULT"
}

Response (2 tabs over from the headers tab): none


- Set up any needed inputs/variables
- Update the requests function with the new data/method/endpoint
- update helper text / comments / variable names to make sense for the new script
- test
'''

# Script to update the harvest status of a cloud account

import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

org_id_list = ["divvyorganizationservice:544"]
harvest_status = "DEFAULT" # can be "PAUSED" or "DEFAULT"

# Key for divvy 
api_key = ""

# API URL
base_url = "https://sales-demo.divvycloud.com"

# # Param validation
if not api_key:
    key = getpass.getpass('API Key:')
else:
    key = api_key

if not base_url:
    base_url = input("Base URL (EX: http://localhost:8001 or http://45.59.252.4:8001): ")

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'Api-Key': key
}

# Set harvest status
def set_status():
    data = {
        "resource_ids": org_id_list,
        "status": harvest_status
    }

    try:
        response = requests.post(
            url=base_url + '/v2/public/clouds/status/set',
            data=json.dumps(data),
            verify=False,
            headers=headers
            )
        response.raise_for_status()

    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return response #.json()    

# Set status
print(set_status())
