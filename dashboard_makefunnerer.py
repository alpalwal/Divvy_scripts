# Create users without MFA and direct permissions 
# Cloud user with direct permissions
# SG exposing SSH

# Networks without traffic logging
# Cloud policy with full access

import boto3
import json
import random


# Boto setups
boto3.setup_default_session(region_name='us-west-1')

# iam_resource = boto3.resource('iam') #using resource representing IAM (for create user)
iam_client = boto3.client('iam') # IAM low level client object (for policy attachment)
ec2_client = boto3.resource('ec2')

# Mix up how many resources to create
def random_number(upper_limit):
    number = random.randint(50, upper_limit)
    return number

# Get a random string without repeating letters for the resource name
def get_random_string():
    letters = "abcdefghijklmnopqrstuvwxyz"
    result_str = ''.join(random.sample(letters, 10))
    return result_str

# Create IAM user
def create_user():
    username = "dashboardresource-" + get_random_string()
    created_user = iam_client.create_user(
        UserName=username    
    )
    return created_user['User']['UserName']

def attach_user_policy(new_user):
    # Attach policy
    response = iam_client.attach_user_policy(
        UserName = new_user, #Name of user
        PolicyArn = 'arn:aws:iam::aws:policy/AdministratorAccess'
        # Policy ARN which you want to asign to user
    )
    return

def create_sg():
    sg_name = "dashboardresource-" + get_random_string()

    sec_group = ec2_client.create_security_group(
        GroupName=sg_name, 
        Description='Dashboard demo SG', 
        VpcId="vpc-ed324b88"
    )

    sec_group.authorize_ingress(
        CidrIp='0.0.0.0/0',
        IpProtocol='tcp',
        FromPort=22,
        ToPort=3389
    )
    return sec_group.id

def lambda_handler(event, context):
    number = random_number(300)
    print("Generating " + str(number) + " users with admin access")
    for x in range(number):
        # Create X new users
        new_user = create_user()
        print("Created user: " + new_user)
        
        # Attach the admin access policy to the new user
        attach_user_policy(new_user)

    number = random_number(300)
    print("Generating " + str(number) + " SGs with 22-3389 exposed")
    for x in range(number):
        # Create sec group
        print(create_sg())
    
    return
 