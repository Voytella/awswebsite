#!/bin/bash
region='us-east-1'
src_dir="./Website"
bucket_name='www.autodeploytest.link'
hosted_zone_name="autodeploytest.link"
stack_name="s3-static-website"

aws cloudformation create-stack --region ${region} \
--stack-name ${stack_name} --template-body file://s3-static-website.yaml \
--parameters ParameterKey=BucketName,ParameterValue=${bucket_name} \
ParameterKey=HostedZoneName,ParameterValue=${hosted_zone_name}

stack_status=""
while [[ $stack_status != '"CREATE_COMPLETE"' ]] && [[ $stack_status != '"ROLLBACK_COMPLETE"' ]];
do
  stack_status=$(aws cloudformation --region ${region} describe-stacks --stack-name ${stack_name} --query Stacks[0].StackStatus);
  echo "Waiting for stack to complete";
  echo "Stack Status: ${stack_status}"
  sleep 15;
done

echo "stack created. Uploading files now"

./upload_files.py $bucket_name "${src_dir}"

echo "files uploaded"
