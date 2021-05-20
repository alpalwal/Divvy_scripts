# https://github.com/aliyun/aliyun-openapi-python-sdk
# Install the core library before running
#  pip install aliyun-python-sdk-core
#  pip install aliyun-python-sdk-ecs
#  pip install aliyun-python-sdk-rds

# Generate an API key/secret here
# https://usercenter.console.aliyun.com/?spm=5176.doc52740.2.3.QKZk8w#/manage/ak

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest
import json

# Auth info
key = ""
secret = ""

region_list = ["cn-qingdao", "cn-beijing", "cn-zhangjiakou", "cn-huhehaote", "cn-wulanchabu", "cn-hangzhou", "cn-shanghai", "cn-shenzhen", "cn-heyuan", "cn-guangzhou", "cn-chengdu", "cn-hongkong", "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-5", "ap-south-1", "ap-northeast-1", "us-west-1", "us-east-1", "eu-central-1", "eu-west-1", "me-east-1"]

total_instances = 0
total_databases = 0

# Initialize a request and set parameters
instance_request = DescribeInstancesRequest.DescribeInstancesRequest()
db_request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
instance_request.set_PageSize(100)
db_request.set_PageSize(100)


for region in region_list:
    # Initialize AcsClient instance
    client = AcsClient(key,secret,region)
    
    # Get instance info
    instance_response = client.do_action_with_exception(instance_request) 
    json_instance_response = json.loads(instance_response)

    number_of_instances_in_this_region = json_instance_response['TotalCount']
    print(str(number_of_instances_in_this_region) + " instances in " + region)

    # db_response = client.do_action_with_exception(db_request)
    
    total_instances = total_instances + number_of_instances_in_this_region

    # Get db info
    db_response = client.do_action_with_exception(db_request) 
    json_db_response = json.loads(db_response)

    number_of_dbs_in_this_region = json_db_response['TotalRecordCount']
    print(str(number_of_dbs_in_this_region) + " DBs in " + region)

    # db_response = client.do_action_with_exception(db_request)
    
    total_databases = total_databases + number_of_dbs_in_this_region

print("\nTotal number of instances:")
print(total_instances)

print("\nTotal number of DBs:")
print(total_databases)

print("\nTotal number of billable resources:")
print(total_instances + total_databases)

