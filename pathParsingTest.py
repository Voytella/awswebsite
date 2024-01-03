# Given a flat list of directory paths, generate a hierarchical list of
# dictionaries whose values are lists of either further dictionaries or files.

import os.path

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
