#!/bin/bash
region='us-east-1'
src_dir="./Website"
lambda_src_dir="./Lambda"
bucket_name='autodeploytest.link'
hosted_zone_name="autodeploytest.link"
lambda_bucket_name='autodeploytest.link-lambda'
stack_name="s3-static-website"
lambda_stack_name="lambda-function"

#aws cloudformation create-stack --region ${region} \
#--stack-name ${stack_name} --template-body file://s3-static-website.yaml \
#--parameters ParameterKey=BucketName,ParameterValue=${bucket_name} \
#ParameterKey=HostedZoneName,ParameterValue=${hosted_zone_name}

# create a stack
# Arg 1: name of stack
# Arg 2: name of bucket
create_stack() {

    aws cloudformation create-stack --region ${region} \
    --stack-name "$1" --template-body file://"$1".yaml \
    --parameters ParameterKey=BucketName,ParameterValue="$2" \
    ParameterKey=HostedZoneName,ParameterValue=${hosted_zone_name}

    stack_status=""
    while [[ $stack_status != '"CREATE_COMPLETE"' ]];
    do
        stack_status=$(aws cloudformation --region ${region} describe-stacks --stack-name "$1" --query Stacks[0].StackStatus);
        echo "Waiting for stack to complete";
        echo "Stack Status: ${stack_status}"
        sleep 15;
    done
}

# create initial stack
create_stack "$stack_name" "$bucket_name"

#stack_status=""
#while [[ $stack_status != '"CREATE_COMPLETE"' ]];
#do
#  stack_status=$(aws cloudformation --region ${region} describe-stacks --stack-name ${stack_name} --query Stacks[0].StackStatus);
#  echo "Waiting for stack to complete";
#  echo "Stack Status: ${stack_status}"
#  sleep 15;
#done

echo "initial stack created. Uploading files now"

# upload website files
./upload_files.py $bucket_name "${src_dir}"

# upload lambda files
./upload_files.py $lambda_bucket_name "${lambda_src_dir}"

echo "files uploaded"

# create lambda function
create_stack "$lambda_stack_name" "$lambda_bucket_name"

echo "lambda stack created"
