# Automated Deployment

## Purpose

Create the infrastructure needed to allow a user to deploy their own
image-hosting website on AWS with only basic configuration information.

## Requirements

* A static website can be deployed on a fresh AWS account without needing to
  interface directly with AWS configurations.

## Notes

### Initial Investigation

* I found a git repo that already contains the infrastructure needed to use
  CloudFormation to deploy an S3 static website:
  https://github.com/Timothy-Pulliam/cloudformation/tree/main/s3-static-website
* I wanna play with this first and get it working. This is a good start! Once I
  get this basic example working, I'll plug in my S3 static website stuff to
  make sure it's happy. The part I'll have to figure out is the Lambda stuff,
  and associated S3 permissions, I put together to make it automatically update
  when new images are uploaded to the S3 bucket. Once that's figured out, I need
  to make a nice interface for it so we don't have users running scripts and
  messing with configuration files.

### Deploying Simple Static Website

* We need a zone in Route 53 to give the script. I've already got the
  "ryanscoolimages.link" zone, but it's in use. To preserve what I've got and
  keep things simple, I just bought a cheap domain for testing:
  "autodeploytest.link". _(The instructions assume this has already been
  done. This is something we'll need to figure out how to automate.)_
* Looks like there's two places that require manual configuration, the run
  script and CloudFormation template. The configuration we need to worry about
  for automating is the domain chosen by the user. We'll first need to walk the
  user through buying their domain, then take that and plug it into these
  files. That doesn't sound too bad. Let's just do it manually with
  "autodeploytest.link" to try things out.
* The command to create the stack hardcoded the region, so I threw in the
  variable.
* With the stack already created, it had the "ROLLBACK_COMPLETE" status rather
  than the expected "CREATE_COMPLETE" status, so it got stuck. I'll add
  "ROLLBACK_COMPLETE" to the exit condition of the loop.
* That fixed it. I didn't have boto3 installed, though, lol! Lemme get that
  taken care of.
* A'ight, it didn't actually do anything. I suspect this is because it never
  prompted me for any kind of login. Why does it say it created the stack just
  fine then? Hmmmmm.
* Since I'm thinking it might be more straightforward to just direct the users
  to upload the template into CloudFormation directly (this gets around the
  problem of authenticating through a custom web app and the need to create a
  custom web app), I tried doing that. It's yelling at me about CloudFormation
  being unable to support a particular resource import,
  "AWS::Route53::RecordSetGroup". Let's figure out what's up with that.
* Ahhh, looks like I tried to create a stack "With existing resources" rather
  than with "With new resoureces"
  (https://stackoverflow.com/questions/62480645/aws-cloudformation-unable-to-import-resources-of-type-subnetroutetableassociati)!
  I really don't want the users to have to go through all this AWS clicking. I
  really hope this can all be automated cleanly down the road. For now, though,
  we'll just focus on getting the template set up!
* Actually, nah, uploading is lame because I can't use the fancy variables and
  other command line stuff. Let's just stick with figuring out properly logging
  in via the command line.
* Woah! I just realized something! The AWS console has a shell with `aws`,
  `python`, and `boto3` installed! This means I don't have to worry about
  authentication at all if I can get all the set up into some easy-to-copy
  commands! Hmmmmm, I think this might be our cheapest option. I'll clone this
  repo into the CloudShell and try it out there.
* When it gets to the Python script, it fails complaining that the bucket
  doesn't exist. Isn't the point of the CloudFormation stuff to automatically
  create everything? It shows that the stack was created, but it's in
  "ROLLBACK_COMPLETE" status which is red. I guess we've gotta work on the
  template. Progress, though! I like the CloudShell route!