import boto3 
import sys

# regions you operate in
regions = ["us-east-2","us-east-1","us-west-1","us-west-2","ap-southeast-1"]

def account_id_list():
    l = [3456789] # list of accounts
    resp = []
    for item in l:
        resp.append(str(item))
    # add any other accounts
    resp.append("1234")
    return resp

def get_session(account_id, region):
    client = boto3.client('sts')
    response = client.assume_role(
        RoleSessionName=f"DivvyCloudResourceCount",
        RoleArn=f'arn:aws:iam::{account_id}:role/infosec-audit',
        )
    creds = {}
    creds['AccessKeyId'] = response['Credentials']['AccessKeyId']
    creds['SecretAccessKey'] = response['Credentials']['SecretAccessKey']
    creds['SessionToken'] = response['Credentials']['SessionToken']
    boto_session = boto3.session.Session(
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken'],
        region_name = region
        )
    return boto_session

def ec2(boto_session, region):
    print(f"### Starting EC2 List for region: {region} ###")
    ec2client = boto_session.client('ec2', region_name=region)
    response = ec2client.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_list.append(instance["InstanceId"] + " , " + region)
            print(f"{instance["InstanceId"]} , {region}")
    return instance_list

def rds(boto_session, region):
    print(f"### Starting RDS List for region: {region} ###")
    rds = boto_session.client('rds', region_name=region)
    response = rds.describe_db_instances()
    for db_instance in response['DBInstances']:
        print(db_instance['Endpoint']['Address'])
        rds_list.append(db_instance['Endpoint']['Address'])
    return rds_list

def redshift(boto_session, region):
    print(f"### Starting Redshift List for region: {region} ###")
    redshiftclient = boto_session.client('redshift', region_name=region)
    response = redshiftclient.describe_clusters()
    for cluster in response["Clusters"]:
        redshift_cluster_list.append(cluster['ClusterIdentifier'] + " , " + region)
        print(cluster['ClusterIdentifier'] + " , " + region)
    return redshift_cluster_list

def elasticache(boto_session, region):
    print(f"### Starting Elasticache List for region: {region} ###")
    elasticacheclient = boto_session.client('elasticache', region_name=region)
    response = elasticacheclient.describe_cache_clusters()
    for cluster in response["CacheClusters"]:
        elasticache_cluster_list.append(cluster['CacheClusterId'] + " , " + region)
        print(f"{cluster['CacheClusterId']} , {region}")
    return elasticache_cluster_list

# def dynamodb(boto_session, region):
#     print("### Starting DynamoDB List for region: " + region + " ###")
#     dynamodbclient = boto_session.client('dynamodb', region_name=region)
#     response = dynamodbclient.list_tables()
#     for table in response["TableNames"]:
#         dynamodb_table_list.append(table + " , " + region)
#         print(f"{table} , {region}")
#     return dynamodb_table_list

def documentdb(boto_session, region):
    documentdb_regions = ["us-east-1","us-west-2"]
    if region in documentdb_regions:
        print(f"### Starting DocumentDB List for region: {region} ###")
        documentdbclient = boto_session.client('docdb', region_name=region)
        response = documentdbclient.describe_db_clusters()
        for documentdb in response["DBClusters"]:
            documentdb_list.append(documentdb['DBClusterIdentifier'] + " , " + region)
            print(f"{documentdb['DBClusterIdentifier']} , {region}")
    else:
        print(f"DocumentDB not supported in {region}. Skipping")
    return documentdb_list

for account in account_id_list():
    print(f"\n%%%%%%%%%%%%%%% {account} %%%%%%%%%%%%%%%%\n")
    instance_list = []
    rds_list = []
    redshift_cluster_list = []
    elasticache_cluster_list = []
    # dynamodb_table_list = []
    elasticsearch_domain_list = []
    workspaces_list = []
    documentdb_list = []
    for region in regions:
        try:
            boto_session = get_session(account, region)
            instance_list = ec2(boto_session, region)
            rds_list = rds(boto_session, region)
            redshift_cluster_list = redshift(boto_session, region)
            elasticache_cluster_list = elasticache(boto_session, region)
            # dynamodb_table_list = dynamodb(boto_session, region)
            documentdb_list = documentdb(boto_session, region)
        except:
            print(f"Skipping {account} in {region}")
    instance_count = len(instance_list)
    rds_count = len(rds_list)
    redshift_cluster_count = len(redshift_cluster_list)
    elasticache_cluster_count = len(elasticache_cluster_list)
    # dynamodb_cluster_count = len(dynamodb_table_list)
    documentdb_count = len(documentdb_list)
    print("\n########### OVERALL COUNTS #############")
    print(f"EC2 Instances in this account: {instance_count}")
    print(f"RDS Instances in this account: {rds_count}")
    print(f"Redshift Clusters in this account: {redshift_cluster_count}")
    print(f"Elasticache Clusters in this account: {elasticache_cluster_count}")
    # print(f"DynamoDB Clusters in this account: {dynamodb_cluster_count}")
    print(f"DocumentDBs in this account: {documentdb_count}")
    total_counts_list = [instance_count,rds_count,redshift_cluster_count,elasticache_cluster_count,documentdb_count]
    total_count = sum(total_counts_list)
    print(f"\n### TOTAL BILLABLE RESOURCE COUNT: {total_count}")