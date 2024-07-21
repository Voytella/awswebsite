#!/bin/bash
region='us-east-1'
src_dir="./Website"
lambda_src_dir="./Lambda"
bucket_name='www.autodeploytest.link'
hosted_zone_name="autodeploytest.link"
lambda_bucket_name='www.autodeploytest.link-lambda'
stack_name="s3-static-website"
lambda_stack_name="lambda-function"


# ----------BEGIN FUNCTIONS----------

# watch the progress of stack creation
# Arg 1: name of stack
watch_stack_creation() {
    stack_status=""
    while [[ $stack_status != '"CREATE_COMPLETE"' ]];
    do
        stack_status=$(aws cloudformation --region ${region} describe-stacks --stack-name "$1" --query Stacks[0].StackStatus);
        echo "Waiting for stack to complete";
        echo "Stack Status: ${stack_status}"
        sleep 15;
    done
}

# -----------END FUNCTIONS-----------

# create the stack for the website
aws cloudformation create-stack --region ${region} \
--stack-name ${stack_name} --template-body file://s3-static-website.yaml \
--parameters ParameterKey=BucketName,ParameterValue=${bucket_name} \
ParameterKey=HostedZoneName,ParameterValue=${hosted_zone_name}

# watch initial stack
watch_stack_creation "$stack_name"

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

# create lambda stack
aws cloudformation create-stack --region ${region} \
--stack-name ${lambda_stack_name} --template-body file://lambda-function.yaml \
--parameters ParameterKey=BucketName,ParameterValue=${lambda_bucket_name} \
--capabilities CAPABILITY_NAMED_IAM

watch_stack_creation "$lambda_stack_name"

echo "lambda stack created"
