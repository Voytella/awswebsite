# Given a flat list of directory paths, generate a hierarchical list of
# dictionaries whose values are lists of either further dictionaries or files.

import os.path

from functools import reduce
from pathlib import PurePath

# hard-coded name of root directory in S3 bucket
ROOT_DIR = "data/"

# simulated return from an S3 query
RAW_SAMPLE_PATHS = ["data/",
                "data/img1.jpg", 
                "data/img2.png",
                "data/folder1/",
                "data/folder1/img3.jpg",
                "data/folder1/img4.png",
                "data/folder1/folder2/",
                "data/folder1/folder2/img5.png",
                "data/folder3/",
                "data/folder3/img6.png"]

# trim the root directory from obtained paths and get rid of empty strings
samplePaths = [path.split(ROOT_DIR)[1] for path in RAW_SAMPLE_PATHS if 
               path.split(ROOT_DIR)[1]]

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
                
    # combine both lists (at end, "branches" will be empty) and return
    return leaves + branches

## flatten a list
#def flatten(nestedList):
#
#    # initialize a new blank list
#    flattenedList = []
#    
#    # go over each element in the provided list
#    for ele in nestedList:
#
#        # if the element is not a list, tack it onto the new list
#        if type(ele) not list:
#            flattenedList = flattenedList + ele
#        
#        # if the element is a list, 
    
# wrap a folder's files
def displayDir(folder, parent):

    # wrap each folder's contents
    for key in folder:
        print("<details>")
        print(f'<summary>{key}</summary>')
        displayHier(folder[key], f'{parent}/{key}')
        print("</details>")

# display the hierarchical data structure
def displayHier(hier, parent):

    # grab any leaves
    leaves = [leaf for leaf in hier if type(leaf) == str]

    # process any encountered branches (nothing is actually returned)
    [displayDir(branch, parent) for branch in hier if type(branch) == dict]

    # after this level's branches have been processed, print the leaves at
    # the bottom
    for leaf in leaves:
        print(f'<img src={parent}/{leaf}>')
