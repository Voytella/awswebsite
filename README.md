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
