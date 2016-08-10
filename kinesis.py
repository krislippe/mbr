import boto3
iam = boto3.client('iam')
firehose = boto3.client('firehose')

with open('/Users/lippek/Documents/weblogs/aws-big-data', 'r') as f:
    for line in f:
        firehose.put_record(
                DeliveryStreamName='MBRwebstream',
                Record={'Data': line}
                )
        print 'Record added'
