import boto3
import json
import io
import os.path

from pathlib import PurePath

# S3 bucket of interest
BUCKET = "ryanscoolimages.link"

# hard-coded name of root directory in S3 bucket
ROOT_DIR = "data/"

# turn flat list of path names into hierarchical list
def hierarchicalize(paths):
    
    # grab any leaves in provided paths list
    leaves = [path for path in paths if not os.path.dirname(path)]
    
    # make a list of dictionaries whose keys are "root" folders
    branches = [{PurePath(branch).parts[0] : hierarchicalize(
        [path.split(branch)[1] for path in paths if
        PurePath(path).parts[0] == PurePath(branch).parts[0] and
        len(PurePath(path).parts) > 1])
        } for branch in paths if
            os.path.dirname(branch) and len(PurePath(branch).parents) == 1]
    
    # combine both lists ("branches" will be empty at end) and return
    return leaves + branches
    
# wrap a folder's files
def displayDir(folder, parent, htmlFile):
    
    # wrap each folder's contents
    for key in folder:
        htmlFile.write(bytes("<details>\n", 'utf-8'))
        htmlFile.write(bytes(f'<summary>{key}</summary>\n', 'utf-8'))
        displayHier(folder[key], f'{parent}/{key}', htmlFile)
        htmlFile.write(bytes("</details>\n", 'utf-8'))
        
# display the hierarchical data structure
def displayHier(hier, parent, htmlFile):
    
    # grab any leaves
    leaves = [leaf for leaf in hier if type(leaf) == str]
    
    # process any encountered branches (nothing is actually returned)
    [displayDir(branch, parent, htmlFile) for branch in hier if 
        type(branch) == dict]
    
    # after this level's branches have been processed, print the leaves at the
    # bottom
    for leaf in leaves:
        htmlFile.write(bytes(f'<img src={parent}/{leaf}>\n', 'utf-8'))

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    # grab all the objects in the root directory of the bucket
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=ROOT_DIR)
    
    # grab the names of all the objects
    rawPaths = [content["Key"] for content in response['Contents']]
    
    # trim off the root directory
    paths = [path.split(ROOT_DIR)[1] for path in rawPaths if
                path.split(ROOT_DIR)[1]]
    
    # initialize new 'index.html' file to be written
    newIndexHTML = io.BytesIO()
    newIndexHTML.write(bytes("<html>\n", 'utf-8'))
    newIndexHTML.write(bytes("<h1>Ryan's Cool Images</h1>\n", 'utf-8'))
    
    # organize the flat list into a hierarchical data structure
    hier = hierarchicalize(paths)
    
    # display the hierarchical data structure as HTML code
    displayHier(hier, os.path.dirname(ROOT_DIR), newIndexHTML)
    
    # close off the HTML file
    newIndexHTML.write(bytes("</html>\n", 'utf-8'))
    
    # rewind the byte file IO stream before upload
    newIndexHTML.seek(0)
    
    # upload the new index.html file to the S3 bucket
    s3.put_object(Body=newIndexHTML, Bucket=BUCKET, Key="index.html",
                    ContentType="text/html")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
