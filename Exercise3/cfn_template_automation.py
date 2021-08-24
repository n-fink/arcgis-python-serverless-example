#!/usr/bin/env python
""" A python script utilizing the Troposphere library to generate a CloudFormation template to deploy a serverless
ArcGIS data update stack
"""

__author__ = "Nick Fink"
__contact__ = "nicholas.fink@nltgis.com"
__copyright__ = "Copyright 2021 New Light Technologies, Inc."
__date__ = "2021/01/26"
__license__ = "MIT"

from troposphere import events, awslambda, iam, Template, GetAtt

# create a cloudformation template to
template = Template()

# set your variables 
portal_url = "https://YourOrg.maps.arcgis.com"
portal_user = "YourUser"
portal_password = "SuperSecurePassword"
data_url = "https://www3.septa.org/api/TrainView/"
frmt = "CSV"
id = ""
file = "my_awesome_api_test.csv"
cron = "rate(5 minutes)"   # how often the service should update
timeout = 30    # lambda time out length in seconds
mem = 256   # lambda workspace memory size
bucket = "my-unique-bucket-name"   # S3 bucket that hosts your zip archive
key = "arcgisLambda.zip"    # the bucket key of your zip archive object

# these variables are just for naming the various stack pieces
name = str(file).split(".")[0]
name_split = name.split("_")
name_cap = [word.capitalize() for word in name_split]
new_name = "".join(name_cap)
lambda_name = "lambda"+new_name
rule_name = "rule"+new_name
perm_name = "perm"+new_name
role_name = "role"+new_name

# create a new IAM role for the lambda
arcgis_role = template.add_resource(iam.Role(
    role_name,
    Path="/",
    Policies=[iam.Policy(
        PolicyName="root",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["logs:*"],
                "Resource": "arn:aws:logs:*:*:*",
                "Effect": "Allow"
            }]
        })],
    AssumeRolePolicyDocument={
       "Version": "2012-10-17",
       "Statement": [{
           "Action": ["sts:AssumeRole"],
           "Effect": "Allow",
           "Principal": {
               "Service": ["lambda.amazonaws.com"]
           }
       }]
   }))

# create a lambda to run the code
arcgis_lambda = template.add_resource(awslambda.Function(
    lambda_name,
    Code=awslambda.Code(
        S3Bucket=bucket,
        S3Key=key),
    Description="Lambda task that updates {}".format(lambda_name),
    FunctionName=lambda_name,
    Handler="lambda.agol_update",
    Runtime="python3.7",
    Timeout=timeout,
    Role=GetAtt(arcgis_role.title, "Arn"),
    MemorySize=mem,
    Environment=awslambda.Environment(
        Variables={
            "data_url": data_url,
            "portal_url": portal_url,
            "portal_user": portal_user,
            "portal_password": portal_password,
            "portal_item": id,
            "file": file,
            "format": frmt})
))

# create an EventBridge rule to kick off the lambda
arcgis_rule = template.add_resource(events.Rule(
    rule_name,
    ScheduleExpression=cron,
    Description="My Lambda CloudWatch Event",
    State="ENABLED",
    Targets=[
        events.Target(
            "MyLambdaTarget",
            Arn=GetAtt(arcgis_lambda.title, "Arn"),
            Id="MyLambdaId"
        )
    ]
))

# add permissions to the lambda to allow EventBridge to kick it off
arcgis_permission = template.add_resource(awslambda.Permission(
    perm_name,
    FunctionName=GetAtt(arcgis_lambda.title, 'Arn'),
    Action='lambda:InvokeFunction',
    Principal='events.amazonaws.com',
    SourceArn=GetAtt(arcgis_rule.title, 'Arn'),
))

# write the json template to a yaml file
template.to_yaml()
fh = open("template.yaml", "w")
fh.writelines(template.to_yaml())
fh.close()
