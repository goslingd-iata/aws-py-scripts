#!/usr/bin/env python3
import sys
import boto3

def chunks(l, n):
    for i in range(0, n):
        yield l[i::n]

cycle = ['|', '/', '-', '\\']

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')

response = ec2.describe_instances(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': ['aws-mrsapapp1', 'aws-mrsapapp3']
        }
    ]
)

instancelist = []
for reservation in (response["Reservations"]):
    for instance in reservation["Instances"]:
        instancelist.append(instance["InstanceId"])


paginator = cloudwatch.get_paginator('describe_alarms')
response = paginator.paginate(
    MaxRecords=20
)

count = 0

alarmslist = []
for page in response:
    for alarm in page['MetricAlarms']:
        sys.stdout.write('\rChecking alarms ' +
                         cycle[int(count/4) % len(cycle)])
        sys.stdout.flush()
        count += 1
        for dimension in alarm['Dimensions']:
            if dimension['Name'] == "InstanceId":
                if dimension['Value'] in instancelist:
                    alarmslist.append(alarm['AlarmName'])

sys.stdout.write('\r                 \r')

if alarmslist:
    print("The following alarms will be disabled:")
    for alarm in alarmslist:
        print(alarm)

    alarmschunks = list(chunks(alarmslist, int(len(alarmslist)/100)+1))

    for alarmschunk in alarmschunks:
        response = cloudwatch.disable_alarm_actions(
            AlarmNames=alarmschunk
        )

    print('Done!')
else:
    print('Nothing to do!')
