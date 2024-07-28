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

We need a zone in Route 53 to give the script. I've already got the
"ryanscoolimages.link" zone, but it's in use. To preserve what I've got and
keep things simple, I just bought a cheap domain for testing:
"autodeploytest.link". _(The instructions assume this has already been
done. This is something we'll need to figure out how to automate.)_

Looks like there's two places that require manual configuration, the run
script and CloudFormation template. The configuration we need to worry about
for automating is the domain chosen by the user. We'll first need to walk the
user through buying their domain, then take that and plug it into these
files. That doesn't sound too bad. Let's just do it manually with
"autodeploytest.link" to try things out.

The command to create the stack hardcoded the region, so I threw in the
variable.

With the stack already created, it had the "ROLLBACK_COMPLETE" status rather
than the expected "CREATE_COMPLETE" status, so it got stuck. I'll add
"ROLLBACK_COMPLETE" to the exit condition of the loop.

That fixed it. I didn't have boto3 installed, though, lol! Lemme get that
taken care of.

A'ight, it didn't actually do anything. I suspect this is because it never
prompted me for any kind of login. Why does it say it created the stack just
fine then? Hmmmmm.

Since I'm thinking it might be more straightforward to just direct the users
to upload the template into CloudFormation directly (this gets around the
problem of authenticating through a custom web app and the need to create a
custom web app), I tried doing that. It's yelling at me about CloudFormation
being unable to support a particular resource import,
"AWS::Route53::RecordSetGroup". Let's figure out what's up with that.

Ahhh, looks like I tried to create a stack "With existing resources" rather
than with "With new resoureces"
(https://stackoverflow.com/questions/62480645/aws-cloudformation-unable-to-import-resources-of-type-subnetroutetableassociati)!
I really don't want the users to have to go through all this AWS clicking. I
really hope this can all be automated cleanly down the road. For now, though,
we'll just focus on getting the template set up!

Actually, nah, uploading is lame because I can't use the fancy variables and
other command line stuff. Let's just stick with figuring out properly logging
in via the command line.

Woah! I just realized something! The AWS console has a shell with `aws`,
`python`, and `boto3` installed! This means I don't have to worry about
authentication at all if I can get all the set up into some easy-to-copy
commands! Hmmmmm, I think this might be our cheapest option. I'll clone this
repo into the CloudShell and try it out there.

When it gets to the Python script, it fails complaining that the bucket
doesn't exist. Isn't the point of the CloudFormation stuff to automatically
create everything? It shows that the stack was created, but it's in
"ROLLBACK_COMPLETE" status which is red. I guess we've gotta work on the
template. Progress, though! I like the CloudShell route!

"ROLLBACK_COMPLETE" means the template's bad; the resources described in the
template couldn't be created for one reason or another. I guess let's take a
close look at our template and compare it to the original from the Medium post.

I took a look at the Events associated with the failing Stack to see what's
going on. It says that "Bucket cannot have ACLs set with ObjectOwnership's
BucketOwnerEnforced setting". Let's find out what that's all about!

Looks like the template does things an old way that don't work anymore I found a
StackOverflow article on an appropriate replacement:
https://stackoverflow.com/questions/76097031/aws-s3-bucket-cannot-have-acls-set-with-objectownerships-bucketownerenforced-s
Let's see if that works!

Success! We've deployed a test static website! Now let's try adding Lambda
functions to the template.

I have lots of questions. Let's start by creating a blank Lambda function in the
template.

Just realized I'll need to call CloudFormation twice. The Lambda function needs
to be told where the execution code is, and the execution code needs to be
uploaded. I'll need to do everything except make the Lambda function, push up
all the files, then create the Lambda function. Not a big deal, just something
to do.

After much tinkering, I was ready to test again! As expected, got some errors.
The first complaint is that there's an "invalid template resource property",
"Policies". Let's tear up the template and see about tidying that up first.

LOL, indentation error. Let's try again.

New error! It's complaining that it needs the "[CAPABILITY_NAMED_IAM]", whatever
that is. Let's find out!

I forgot to remove the duplicated role from the other template file.

The lambda template is failing validation. Let's work through this.

I got it to where it's failing due to some capabilities thing. Not sure what
that means, and it'll require some investigation. I'll call it for today and
pick back up tomorrow!

Just picked back up. It's complaining that a stack with id "lambda-function"
doesn't exist. Looks like I forgot to clean something up somewhere. Let's take a
look!

Ah! The stack creation failed, so the expected stack was never created. Gotcha.
It says "Parameter values specified for a template which does not require them."
Maybe my copy-paste was a bit overzealous? Let's take a look at the template for
the Lambda function and accompanying pieces.

Yup! Overzealous copy-paste. I was passing a "parameters" flag when creating the
stack, and the template does not contain a "Parameters" section for receiving
them! I just commented out that line. Let's try again!

I guess just commenting it out broke the flow of the command. Lemme just
straight up remove it.

Next is an error when trying to spin up the Lambda stack. I forgot the "www".
Let's try again.

It made the website and lambda stacks, but it's behaving strangely. When I try
to look at the logs, is complains that the log group for the new Lambda function
doesn't exist. Which is true! How come the logs aren't showing up? (I need the
logs to figure out why it's not updating when I upload an image, lol!) I also
need to initialize the thing with a 'data/image.png' file or something to make
sure the proper directory is created first thing.

They said logs won't exist until it runs and makes some, which makes sense.
Unfortunately, it's not running when I upload a new file! Why's it not
triggering? Ahhh! Perhaps because it doesn't look like any trigger's been
configured! We've gotta do that separately, I guess. Cool, let's figure it out!

Alright, I added in a bunch of stuff ChatGPT suggested. Let's see if this works!

Just dealing with some formatting issues. I'm working through validating the
template.

Fixed the formatting! Looks like it's particular about the filters for the S3
Event Configuration. I'll make sure it's named "prefix".

Now it doesn't like something about a handler. Let's investigate that.

Something in the Lambda template is invalid. I'm just gonna comment out the new
requests one at a time and go down the list.

Lol, what I meant was comment them all out, verify the old stuff still works,
then uncomment them one at a time! The S3EventNotification seems to be stuck on
creation, it's been there for a few minutes.

Yeah, it's just busted. I found in the Bucket configuration in the GUI where the
Event Notifications are configured, though. 

Nope, still busted! Let's try the route of getting a YAML export of our
existing, working configuration.
