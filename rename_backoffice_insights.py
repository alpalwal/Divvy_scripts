# Script to clone insights and packs from one Divvy install to another.

# How to run:
# This can be ran from any system that has access to the DivvyCloud instance (including the one that's running Divvy)

# For Mac:
# sudo pip3 install requests
# python3 clone_all_backoffice_insights.py

# For PC:
# python.exe -m pip install requests
# python.exe clone_all_backoffice_insights.py

import json
import requests
import getpass

requests.packages.urllib3.disable_warnings() # throws warnings otherwise

# Username/password to authenticate against the API
username = ""
password = "" # Leave this blank if you don't want it in plaintext and it'll prompt you to input it when running the script.

# API URLs
base_url = ""

# Param validation
if not base_url:
    print("Please set the base URLs in the paramters. (Lines ~27) Exiting")
    exit()

if not username:
    username = input("Original Environment Username: ")

if not password:
    passwd = getpass.getpass('Original Environment Password:')
else:
    passwd = password

insight_names = [
    { "new_name": "[CPU-1] Monitor missing Endpoint Protection in Azure Security Center",    "backoffice_id": 148,    "old_name":"Security Center Endpoint Protection Recommendation Is Off"},
    { "new_name": "[CPU-2] System updates should be installed on your machines",    "backoffice_id": 146,    "old_name":"Security Center System Updates Recommendation Is Off"},
    { "new_name": "[CPU-3] Vulnerabilities in security configuration on your machines should be remediated",    "backoffice_id": 147,    "old_name":"Security Center Security Configurations Recommendation Is Off"},
    { "new_name": "[CPU-6] Endpoint protection solution should be installed on virtual machine scale sets",    "backoffice_id": 509  ,    "old_name":"Instance Does Not Have Endpoint Protection Installed"},
    { "new_name": "[CPU-7] System updates on virtual machine scale sets should be installed",    "backoffice_id": 542,    "old_name":"Autoscaling Group Automatic OS Upgrades Enabled"},
    { "new_name": "[CPU-8] Disk encryption should be applied on virtual machines - Sec Center",    "backoffice_id": 149,    "old_name":"Security Center Disk Encryption Recommendation Is Off"},
    { "new_name": "[CPU-8] Disk encryption should be applied on virtual machines - Azure Sec 7.1",    "backoffice_id": 197,    "old_name":"Instance OS Disk Not Encrypted"},
    { "new_name": "[CPU-8] Disk encryption should be applied on virtual machines - Azure Sec 7.2",    "backoffice_id": 198,    "old_name":"Data Disks Not Encrypted"},
    { "new_name": "[CPU-9] Vulnerabilities should be remediated by a Vulnerability Assessment solution",    "backoffice_id": 153,    "old_name":"Security Center Vulnerability Assessment Recommendation Is Off"},
    { "new_name": "[CPU-10] Adaptive Application Controls should be enabled on virtual machines",    "backoffice_id": 156,    "old_name":"Security Center Adaptive Application Controls Recommendation Is Off"},
    { "new_name": "[CPU-13] Diagnostic logs in Service Bus should be enabled",    "backoffice_id": 540  ,    "old_name":"Message Queue Invalid Diagnostic Logging Configuration"},
    { "new_name": "[CPU-21] CORS should not allow every resource to access your Function App",    "backoffice_id": 560,    "old_name":"Web App Cross Origin Resource Sharing allows access from all Domains"},
    { "new_name": "[CPU-23] Remote debugging should be turned off for API App",    "backoffice_id": 561,    "old_name":"Web App with Remote Debugging Turned On"},
    { "new_name": "[CPU-27] Role-Based Access Control should be used on Kubernetes Services",    "backoffice_id": 186,    "old_name":"Cluster not using Role-Based Access Control"},
    { "new_name": "[CPU-29] Authorized IP ranges should be defined on Kubernetes Services",    "backoffice_id": 555,    "old_name":"Cluster without Authorized IP Ranges"},
    { "new_name": "[CPU-30] Kubernetes Services should be upgraded to a non-vulnerable Kubernetes version",    "backoffice_id": 554,    "old_name":"Cluster not Upgraded to the Latest Version"},
    { "new_name": "[CPU-31] Preview - Enable the built-in vulnerability assessment solution on virtual machines",    "backoffice_id": 552,    "old_name":"Instance Without Vulnerability Assessment Extension"},
    { "new_name": "[NET-32] Subnets should be associated with a Network Security Group",    "backoffice_id": 557,    "old_name":"Private Subnet not associated with an Access List"},
    { "new_name": "[NET-34] Internet-facing virtual machines should be protected with Network Security Groups",    "backoffice_id": 553,    "old_name":"Instance Without Access List Assignment"},
    { "new_name": "[NET-35] Monitor unprotected network endpoints in Azure Security Center",    "backoffice_id": 200,    "old_name":"Virtual Machine Endpoint Protection Extension Not Installed"},
    { "new_name": "[NET-38] DDoS Protection Standard should be enabled",    "backoffice_id": 508,    "old_name":"Network Without DDoS Protection Enabled"},
    { "new_name": "[NET-39] Management ports should be closed on your virtual machines",    "backoffice_id": 551,    "old_name":"Instance Exposing Management Ports"},
    { "new_name": "[NET-40] IP Forwarding on your virtual machine should be disabled",    "backoffice_id": 228,    "old_name":"Instance With IP Forwarding Enabled"},
    { "new_name": "[DATA-41] Secure transfer to storage accounts should be enabled",    "backoffice_id": 293,    "old_name":"Storage Account Not Enforcing Transit Encryption"},
    { "new_name": "[DATA-42] Audit provisioning of an Azure Active Directory administrator for SQL server",    "backoffice_id": 210,    "old_name":"Database Instance Azure Active Directory Admin Not Configured"},
    { "new_name": "[DATA-43] Only secure connections to your Redis Cache should be enabled",    "backoffice_id": 105,    "old_name":"Cache Instance Transit Encryption Disabled"},
    { "new_name": "[DATA-44] Monitor unaudited SQL servers in Azure Security Center",    "backoffice_id": 157,    "old_name":"Security Center SQL Auditing & Threat Detection Recommendation Is Off"},
    { "new_name": "[DATA-45] Transparent Data Encryption on SQL databases should be enabled",    "backoffice_id": 158,    "old_name":"Security Center SQL Encryption Recommendation Is Off"},
    { "new_name": "[DATA-47] Diagnostic logs in Azure Data Lake Store should be enabled",    "backoffice_id": 538,    "old_name":"Data Lake Storage Invalid Diagnostic Logging Configuration"},
    { "new_name": "[DATA-48] Diagnostic logs in Event Hub should be enabled",    "backoffice_id": 537,    "old_name":"Data Stream Invalid Diagnostic Logging Configuration"},
    { "new_name": "[IDEN-59] A maximum of 3 owners should be designated for your subscription",    "backoffice_id": 543,    "old_name":"Cloud Account with More Than Three Account Owners"},
    { "new_name": "[IDEN-60] There should be more than one owner assigned to your subscription",    "backoffice_id": 544,    "old_name":"Cloud Account with Only One Account Owner"},
    { "new_name": "[IDEN-64] audit",    "backoffice_id": 549,    "old_name":"Cloud User is Deprecated"},
    { "new_name": "[IDEN-65] Deprecated accounts with owner permissions should be removed from your subscription",    "backoffice_id": 550,    "old_name":"Cloud User with Owner Permissions is Deprecated"},
    { "new_name": "[IDEN-66] External accounts with owner permissions should be removed from your subscription",    "backoffice_id": 546,    "old_name":"External Cloud User with Owner Permissions"},
    { "new_name": "[IDEN-67] External accounts with write permissions should be removed from your subscription",    "backoffice_id": 548,    "old_name":"External Cloud User with Write Permissions"},
    { "new_name": "[IDEN-68] External accounts with read permissions should be removed from your subscription",    "backoffice_id": 547,    "old_name":"External Cloud User with Read Permissions"},
    { "new_name": "[IDEN-69] Diagnostic logs in Key Vault should be enabled - Azure Security",    "backoffice_id": 539,    "old_name":"Key Vault Invalid Diagnostic Logging Configuration"},
    { "new_name": "[IDEN-69] Diagnostic logs in Key Vault should be enabled - Other Security Considerations",    "backoffice_id": 310,    "old_name":"Key Vault Is Not Recoverable"}
]



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
auth_token = get_auth_token(username,passwd,base_url)

headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'X-Auth-Token': auth_token
}

# list all insights
def list_insights():
    data = {}
    response = requests.get(
        url=base_url + '/v2/public/insights/list',
        data=json.dumps(data),
        headers=headers,
        verify=False
    )
    return response.json()

# Create a custom insight
def create_insight(insight_config,):
    response = requests.post(
        url=base_url + '/v2/public/insights/create',
        data=json.dumps(insight_config),
        headers=headers,
        verify=False
    )
    return response.json()

# Add notes to insight
def add_insight_notes(insight_id,description,):
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

# Create a new pack
def create_pack():
    data = {
        "name": "DHHS security controls",
        # "backoffice": pack['backoffice'],
        # "badges": pack['badges'],
        # "badge_filter_operator": "OR",
        # "custom": [],
        "description": "DHHS security controls"
        }

    response = requests.post(
        url=base_url + '/v2/public/insights/pack/create',
        data=json.dumps(data),
        headers=headers,
        verify=False
    )
    return response.json()

# Add an insight to the pack
def add_insight_to_pack(pack_info,custom_insight_ids,):
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

print("Creating custom pack in new environment")
new_pack_info = create_pack()

print("Generating list of all backoffice insights")
all_insights = list_insights()
backoffice_insights = []
for insight in all_insights:
    if insight["source"] == "backoffice":
        #Clean up unneeded params
        del insight['by_cloud']
        del insight['custom_severity']
        del insight['meta_data']
        del insight['resource_group_blacklist']
        del insight['source']
        del insight['results']
        del insight['total']
        del insight['all']
        del insight['updated_at']
        del insight['inserted_at']
        del insight['exemptions']
        del insight['by_type']
        del insight['by_resource_group']
        del insight['cache_updated_at']
        del insight['duration']
        del insight['author']
        del insight['favorited']
        del insight['bots']
        insight['template_id'] = None ## not sure why this is required
        insight['scopes'] = []
        backoffice_insights.append(insight)

insights_to_add = []

print("Adding insights to new environment")
for new_insight in insight_names:
    for old_insight in backoffice_insights:
        if old_insight['insight_id'] == new_insight['backoffice_id']:
            print("Creating new insight: " + new_insight['new_name'] + " ID = " + str(old_insight['insight_id']))
            print("Old insight name = " + old_insight['name'])

            old_insight['name'] = new_insight['new_name']
            new_insight_info = create_insight(old_insight)

            try:
                # Add notes to the insight and add to the list of insights to add to the new pack
                add_insight_notes(new_insight_info['insight_id'],old_insight['description'])
                insights_to_add.append(new_insight_info['insight_id'])
            except:
                print("Unexpected error. Skipping.")
                print("Insight name: " + old_insight['name'])
                # print(new_insight_info)


print("")
if insights_to_add:
    print("Adding custom insights")
    add_insight_to_pack(new_pack_info,insights_to_add)
    print("Done")
else:
    print("No custom insights to add for this pack. Skipping")
