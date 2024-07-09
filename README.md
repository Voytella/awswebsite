# AWS Website

## Purpose

Create a webpage that mimics an FTP server.

## Requirements

* the webpage displays a directory tree
* the webpage is automatically updated when the directory tree is modified

## Bonus Requirements

* the URL is customizable

## Notes

### Detecting Change in S3 Bucket

* I'm thinking we can use EventBridge to listen for changes to the S3
  bucket. When a change is detected, a Lambda function is run that will generate
  a new `index.html` file that reflects the changes made. The new `index.html`
  will then be uploaded to the S3 bucket and replace the old one. Let's start by
  making a "hello world" Lambda function and getting it triggered by an S3
  bucket update.
  
* Never mind, that'd end up with recursive updates each time the `index.html`
  changes. Can I ask it to ignore that particular file?
  
* Yes! I made a directory in the bucket called `data`, and the Lambda function
  only triggers on changes made to that directory. `index.html` is in the
  root. Cool! I also verified that the Lambda function triggers properly when
  updates are made to `data`. Now let's figure out how to capture the output of
  the Lambda function so we can debug creating the new `index.html`.
  
* Alright, it's literally just a `print` statement and we can view everything in
  CloudWatch. Cool! Now let's figure out how to get the directory tree of the S3
  bucket. 
  
* Don't forget to configure the S3 bucket so that it will allow the service user
  running the Lambda function to access it! With that error fixed, it looks like
  `get_object` only does one object. Let's find the function we need to
  recursively get the names of objects in a directory.
  
* We've got a list of objects prefixed with "data/"! (Including "data/" itself,
  which will be helpful for pathing.) The next step will just be some creative
  Python to wrap all that up in a nice HTML file! After that all we'll need to
  do is upload the new to replace the old, and we'll be set!

### Generating HTML File

* We're able to get a list of all the names in the `data/` directory in the S3
  bucket. These names are in a flat list. We can parse paths with `os.path`
  (https://docs.python.org/3/library/os.path.html). I'd like to organize things
  in a tree where each level of branch is a dropdown menu ending with the
  leaves, which are just displayed. I'd like to try doing this by organizing the
  flat list of directory paths into a hierarchical list of dictionaries, with
  each level of Key corresponding to a directory level. This data structure will
  be a list of dictionaries whose values are lists, either of further
  dictionaries or of files (leaves). Let's start by using `os.path` to convert a
  flat list of directory paths into this hierarchical list of dictionaries.
  
* Success! Now I need to figure out how to traverse it nicely, then we can put
  in the HTML decorations.

* When parsing the data structure, there are three different types of elements
  in the list we need to handle:
  1. String: Just straight print it out.
  2. Dictionary: This means a folder has been encountered. The elements in the
     folder will need to be wrapped in HTML, so we need a special function to do
     this wrapping for us. A separate function will be called to handle the
     wrapping for each key in the dictionary. The values will be processed with
     the regular data structure processing function.
   3. List: Recursively call the data structure processing function, feeding it
      the encountered list.
      
* I realized since we're just printing HTML code, we don't have to go through
  the hassle of actually flattening out everything on the back end. Yay
  shortcuts! I've got everything worked out. Now let's add the HTML decorations
  and test it out!
  
* Looks like we're looking for the `<details>` HTML element for the thing I had
  in mind.
  
* Cool! We've got something! Now let's throw it into AWS to see if it works.

* Got it! It writes the HTML to the logs! Now we just need to figure out how to
  write that output to a file and send it over to S3. To do that, it looks like
  we'll need to make a file object and write our HTML to it.
  
* I accidentally tried to write a file to the filesystem. Can we do a thing
  where we just make a giant string and write that out?

* I messed up. I forgot the paths to the image sources needed to be
  absolute. RIP. Let's see if we can turn this around.

* Alright that crisis has been averted. Now we're running into issues getting
  the HTML file to render properly. Let's add little-by-little things to a test
  `index.html` file to see where things break down.
  
* I tried manually uploading an HTML file with the same kind of code, and it
  worked just fine. I think there's something crazy going on with how I'm
  uploading the generated HTML file into S3. Let's see what's up with all that.
  
* Success! We just needed to set the "ContentType" in the "put_object" call to
  "text/html". Nice! Now let's dabble in customizing the URL.
  
# Customizing the URL

* We need to use AWS Route 53 to register a domain. Let's give it a shot!

* I bought "ryanscoolimages.link" for a year for $5 

* Success! I followed this tutorial to link the domain to my S3 bucket: https://docs.aws.amazon.com/AmazonS3/latest/userguide/website-hosting-custom-domain-walkthrough.html

# Creating Template

* We can use AWS CloudFormation to create deployable templates of AWS
  configurations. I need to create a CloudFormation template that configures S3,
  Lambda, and Route 53 to deploy a webpage.
* In the template, the user would be presented with a prompt to choose and
  purchase a domain. The template will then take that single piece of info and
  generate the rest of the environment with the other services.
* First thing I need to do is figure out how AWS CloudFormation works, lol!
  Let's see about starting with a basic tutorial.

# Known Bugs / Limitations

* Spaces in folder names breaks things.
* Only images are assumed to exist within the bucket.
* Only images will be displayed
