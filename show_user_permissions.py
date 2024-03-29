# Script to list all permissions a user has via groups and roles

##### SAMPLE OUTPUT
'''
[Alex-MBP scripts]$python show_user_permissions.py 
User: ben.calpotura
Number of attached groups: 3
Roles for group: Marketing Team
[]
Roles for group: DivvySales
[   {   'add_cloud': False,
        'all_permissions': False,
        'badge_scopes': [],
        'cloud_scopes': [],
        'delete': False,
        'description': 'Testing role',
        'global_scope': True,
        'groups': ['divvyusergroup:39', 'divvyusergroup:45'],
        'manage': True,
        'name': 'Global View-Provision-Manage',
        'provision': True,
        'resource_group_scopes': [],
        'resource_id': 'divvyrole:1:25',
        'view': True},
    {   'add_cloud': False,
        'all_permissions': False,
        'badge_scopes': [],
        'cloud_scopes': [],
        'delete': False,
        'description': 'DivvyCloud Sales Team role',
        'global_scope': True,
        'groups': ['divvyusergroup:45'],
        'manage': True,
        'name': 'DivvySales',
        'provision': True,
        'resource_group_scopes': [],
        'resource_id': 'divvyrole:1:34',
        'view': True}]
Roles for group: Group Curation
[   {   'add_cloud': False,
        'all_permissions': False,
        'badge_scopes': [],
        'cloud_scopes': [],
        'delete': False,
        'description': 'Curate into whitelist RG',
        'global_scope': False,
        'groups': ['divvyusergroup:52', 'divvyusergroup:64'],
        'manage': True,
        'name': 'Resource Group Curation',
        'provision': False,
        'resource_group_scopes': ['resourcegroup:64:'],
        'resource_id': 'divvyrole:1:53',
        'view': True}]
'''


import json
import requests
import getpass
import pprint
pp = pprint.PrettyPrinter(indent=4)

requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

# Key for the 
api_key = ""

# API URL
base_url = ""

# User in DivvyCloud
divvy_user = ""

# # Param validation
if not divvy_user:
    divvy_user = input("Username in DivvyCloud: ")

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



# Get User info
def get_users():
    data = {}
    response = requests.get(
        url=base_url + '/v2/public/users/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()    

# Get User info
def get_group_info(user_id):
    data = {}
    response = requests.post(
        url=base_url + '/v2/prototype/user/divvyuser:' + user_id + ':/groups/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
        )
    return response.json()        

# Create the pack
user_list = get_users()
#print(user_list)

for user_info in user_list['users']:
    username = user_info['username']
    if username == divvy_user:
        # List group info for the user
        group_info = get_group_info(str(user_info['user_id']))
        print("User: " + username)
        print("Number of attached groups: " + str(len(group_info['groups'])))

        for group in group_info['groups']:
            print("Roles for group: " + group['name'])
            #print(group['roles'])
            pp.pprint(group['roles'])

