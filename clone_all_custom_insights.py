# Script to clone insights and packs from one Divvy install to another.

# How to run:
# This can be ran from any system that has access to the DivvyCloud instance (including the one that's running Divvy)

# For Mac:
# sudo pip3 install requests
# python3 clone_all_custom_insights.py

# For PC:
# python.exe -m pip install requests
# python.exe clone_all_custom_insights.py

# INSIGHT SCOPES ARE NOT SAVED

import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # throws warnings otherwise

# Username/password to authenticate against the API
old_env_username = ""
old_env_password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 
new_env_username = ""
new_env_password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script. 

# API URLs
old_env_base_url = ""
new_env_base_url = ""

# Param validation
if not old_env_base_url or not new_env_base_url:
    print("Please set the base URLs in the paramters. (Lines ~29/30) Exiting")
    exit()

if not old_env_username:
    old_env_username = input("Original Environment Username: ")

if not old_env_password:
    old_env_passwd = getpass.getpass('Original Environment Password:')
else:
    old_env_passwd = old_env_password

if not new_env_username:
    new_env_username = input("New Environment Username: ")

if not new_env_password:
    new_env_passwd = getpass.getpass('New Environment Password:')
else:
    new_env_passwd = new_env_password


# Shorthand helper function
def get_auth_token(username,passwd,base_url):
    response = requests.post(
        url=base_url + '/v2/public/user/login',
        data=json.dumps({"username": username, "password": passwd}),
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        },
        verify=False
        )
        
    return response.json()['session_id']

# Get new auth tokens with new creds
old_env_auth_token = get_auth_token(old_env_username,old_env_passwd,old_env_base_url)
new_env_auth_token = get_auth_token(new_env_username,new_env_passwd,new_env_base_url)


old_env_headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'X-Auth-Token': old_env_auth_token
}

new_env_headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'X-Auth-Token': new_env_auth_token
}

# list all insights
def list_insights(headers,base_url):
    data = {}
    response = requests.get(
        url=base_url + '/v2/public/insights/list',
        data=json.dumps(data),
        headers=headers,
        verify=False
        )
    return response.json()    

# Create a custom insight
def create_insight(insight_config,headers,base_url):
    response = requests.post(
        url=base_url + '/v2/public/insights/create',
        data=json.dumps(insight_config),
        headers=headers,
        verify=False
        )
    return response.json()        

# Add notes to insight
def add_insight_notes(insight_id,description,headers,base_url):
    data = {
        "notes": description
    }
    response = requests.post(
        url=base_url + '/v2/public/insights/' + str(insight_id) + '/notes/update',
        data=json.dumps(data),
        headers=headers,
        verify=False
        )
    return response # No response expected   


# Add notes to insight
def list_packs(headers,base_url):
    response = requests.get(
        url=base_url + '/v2/public/insights/packs/list',
        headers=headers,
        verify=False
        )
    return response.json() # No response expected   

# Create a new pack
def create_pack(pack,headers,base_url):
    data = {
        "name": pack['name'], 
        "backoffice": pack['backoffice'], 
        "badges": pack['badges'],
        "badge_filter_operator": "OR",
        "custom": [], 
        "description": pack['description'],
        "logo_url": pack['logo_url']
    }

    response = requests.post(
        url=base_url + '/v2/public/insights/pack/create',
        data=json.dumps(data),
        headers=headers,
        verify=False
        )
    return response.json()    

# Add an insight to the pack
def add_insight_to_pack(pack_info,custom_insight_ids,headers,base_url):
    data = {
        "name": pack_info['name'], 
        "badge_filter_operator": None,
        "description": pack_info['description'], 
        "logo_url": None, 
        "backoffice": [], 
        "custom": custom_insight_ids,
        "badges": None
    }

    response = requests.post(
        url=base_url + '/v2/public/insights/pack/' + str(pack_info['pack_id']) + '/update',
        data=json.dumps(data),
        headers=headers,
        verify=False
        )
    return response#.json()    

# list all bots
def list_bots(headers,base_url):
    data = {"filters":[],"limit":500,"offset":0}

    response = requests.post(
        url=base_url + '/v2/public/botfactory/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()

# create bot
def create_bot(bot_info,headers,base_url):
    data = bot_info

    response = requests.post(
        url=base_url + '/v2/public/botfactory/bot/create',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()


packs=list_packs(old_env_headers,old_env_base_url)
custom_packs = []
for pack in packs:
    if pack['source'] == "custom":
        print("Custom pack found - " + pack['name'])
        custom_packs.append(pack)

print("Generating list of custom insights")
all_insights = list_insights(old_env_headers,old_env_base_url)
custom_insights = []
for insight in all_insights:
    if insight["source"] == "custom":
        #Clean up unneeded params
        del insight['owner_resource_id']
        del insight['organization_id']
        del insight['resource_group_blacklist']
        del insight['updated_at']
        del insight['tags']
        del insight['user_resource_id']
        del insight['source']
        del insight['results']
        del insight['total']
        del insight['exemptions']
        del insight['duration']
        del insight['author']
        del insight['version']
        del insight['bots']        
        insight['scopes'] = []        
        custom_insights.append(insight)
  
print("Adding insights to new environment")

# Loop through insight_configs and add a filter for each
for insight in custom_insights:
    print("Creating new insight: " + insight['name'])
    new_insight_info = create_insight(insight,new_env_headers,new_env_base_url)
    if 'insight_id' in new_insight_info:
        insight['new_insight_id'] = new_insight_info['insight_id']
        # Add notes to the insight
        add_insight_notes(new_insight_info['insight_id'],insight['description'],new_env_headers,new_env_base_url)  
    else:
        print("Unexpected error. Skipping.")
        print("Insight name: " + insight['name'])
        print(new_insight_info)


print("Getting list of existing custom packs")
list_packs(old_env_headers,old_env_base_url)
for pack in custom_packs:
    print("Creating custom pack in new environment and adding non-custom insights. Name: " + pack['name'])
    new_pack_info = create_pack(pack,new_env_headers,new_env_base_url)

    # Go through packs and add insights to the new packs - map old IDs to new IDs
    insights_to_add = []
    print("Generating list of custom insights to add to pack: " + pack['name'])
    for insight_id_in_custom_pack in pack['custom']:
        for old_custom_insight in custom_insights:
            if insight_id_in_custom_pack == old_custom_insight['insight_id']:
                try:
                    print("Found custom insight to add to pack. Name: " + old_custom_insight['name'])
                    insights_to_add.append(old_custom_insight['new_insight_id'])
                except KeyError:
                    print("Skipping insight that wasn't created earlier. " + str(old_custom_insight))

    print("")
    if insights_to_add:
        print("Adding custom insights")
        add_insight_to_pack(new_pack_info,insights_to_add,new_env_headers,new_env_base_url)
    else:
        print("No custom insights to add for this pack. Skipping")


print("\nStarting bot duplication")

# Create the pack
old_env_bot_list = list_bots(old_env_headers,old_env_base_url)['bots']

print("Number of bots to duplicate: " + str(len(old_env_bot_list)))

for bot in old_env_bot_list:
    print("\nCreating bot " + bot['name'])
    if not bot['insight_id']:
        new_insight_id = None
    elif bot['source'] == "backoffice":
        new_insight_id = bot['insight_id']
    elif bot['source'] == "custom":
        for old_custom_insight in custom_insights:
            if bot['insight_id'] == old_custom_insight['insight_id']:
                try:
                    new_insight_id = old_custom_insight['new_insight_id']
                    break
                except KeyError:
                    print("Error looking up old insight ID to link to the bot. Skipping.")
                    break
    else:
        print(bot)

    new_hookpoints = []
    if bot['hookpoint_created'] == True:
        new_hookpoints.append("divvycloud.resource.created")
    if bot['hookpoint_tags_modified'] == True:
        new_hookpoints.append("divvycloud.resource.tags_modified")
    if bot['hookpoint_modified'] == True:
        new_hookpoints.append("divvycloud.resource.modified")
    if bot['hookpoint_destroyed'] == True:
        new_hookpoints.append("divvycloud.resource.destroyed")

    try:
        new_bot_info = {
            "insight_id": new_insight_id,
            "source": bot['source'],
            "name": bot['name'],
            "description": bot['description'],
            "category": bot['category'],
            "instructions": {
                "groups": [],
                "actions": bot['instructions']['actions'],
                "resource_types": bot['instructions']['resource_types'],
                "badges": [],
                "hookpoints": new_hookpoints,
                "filters": bot['instructions']['filters']
            }
        }

        new_bot_output = create_bot(new_bot_info,new_env_headers,new_env_base_url)
        if new_bot_output['date_created']:
            print("Bot created successfully")

    except Exception as e:
        print("Error while creating bot. Skipping")
        print(e)

