import uuid
import json
import time
import sys
import os
import json
import boto3

def lambda_handler(event, context):
    #generate a uuid
    print(boto3.__version__)
    uuId = str(uuid.uuid4())
    uuidSplit = uuId.split("-")[4]
    bucketName = os.environ['ConnectInstanceName'] + uuidSplit
    instanceAlias = os.environ['ConnectInstanceName']
    conClient = boto3.client('connect') #we will need to specify region on this
    
    #create a connect instance
    conResponse = conClient.create_instance(
        ClientToken=uuId,
        IdentityManagementType=os.environ['Identity'],
        InstanceAlias=instanceAlias, #generates a random instance alias
        InboundCallsEnabled=True,
        OutboundCallsEnabled=True
        )

    #get the arn and ID, we will need those later
    arn = conResponse['Arn']
    connectId = conResponse['Id']

    #Wait maybe? This would be better accomplished with a Step Function
    time.sleep(90)

    # Create S3 Bucket
    s3Client = boto3.client('s3')
    s3response = s3Client.create_bucket(
        ACL='private',
        Bucket=bucketName,
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'
    },
    ObjectLockEnabledForBucket=False
    )

    # get the ARN of AWS issued KMS Key for Connect
    kmsClient = boto3.client('kms')
    kmsResponse = kmsClient.describe_key(
        KeyId='alias/aws/connect'
        )

    print(kmsResponse)
    kmsKeyId = kmsResponse['KeyMetadata']['Arn']
    time.sleep(15)
    
    # Associate Storage, these must be done one at a time
    conStorageResponse = conClient.associate_instance_storage_config(
        InstanceId=connectId,
        ResourceType='CHAT_TRANSCRIPTS',
        StorageConfig={
            'StorageType': 'S3',
            'S3Config': {
                'BucketName': bucketName,
                'BucketPrefix': 'ChatTranscripts',
                'EncryptionConfig': {
                    'EncryptionType': 'KMS',
                    'KeyId': kmsKeyId
                },
            }, 
        }
    )
    conStorageResponse = conClient.associate_instance_storage_config(
        InstanceId=connectId,
        ResourceType='CALL_RECORDINGS',
        StorageConfig={
            'StorageType': 'S3',
            'S3Config': {
                'BucketName': bucketName,
                'BucketPrefix': 'CallRecordings',
                'EncryptionConfig': {
                    'EncryptionType': 'KMS',
                    'KeyId': kmsKeyId
                },
            },
        }
    )
    conStorageResponse = conClient.associate_instance_storage_config(
        InstanceId=connectId,
        ResourceType='SCHEDULED_REPORTS',
        StorageConfig={
            'AssociationId': 'string',
            'StorageType': 'S3',
            'S3Config': {
                'BucketName': bucketName,
                'BucketPrefix': 'Reports',
                'EncryptionConfig': {
                    'EncryptionType': 'KMS',
                    'KeyId': kmsKeyId
                },
            },
        }
    )
    conAddOrigin = conClient.associate_approved_origin(
        InstanceId=connectId,
        Origin= os.environ['Origin']
    )
    #we're done
    return {
        'connectArn': arn,
        'bucketName': bucketName,
        'instanceAlias': instanceAlias,
        'status': 200
    }