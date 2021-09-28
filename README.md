# sam-app

# create an S3 bucket to store SAM package for deployment

aws s3 mb s3://bucket-name --profile aws-profile
# sam package

sam  package --s3-bucket "s3-bucket-name" --template-file "template-file" -name --output-template-file "output-file-name" --profile aws-profile

# sam deploy

sam deploy --template-file "srcout/template-generated.yml" --stack-name "cf-stack-name" --parameter-overrides "Key1=Value1 Key2=Value2" --capabilities CAPABILITY_IAM --profile aws-profile

# sam delete

sam delete --stack-name "stack-name" --profile "aws-profile"