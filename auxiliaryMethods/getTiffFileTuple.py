import os
import re

def getTiffFileTuple( imagePath : str , fileType : str) -> tuple:
    # get all the tiff files in a given folder

    if isinstance(imagePath,str): 
        imagePath = os.path.abspath( imagePath )
    else: raise Exception("'imagePath' is not of type 'str', it is if type %s" %(str(type(imagePath))))

    if isinstance(imagePath,str) and os.path.isfile(imagePath):
        return tuple([imagePath])
    
    # otherwise we presume to have the path to a folder with multiple tiff files
    tiffFileList = []
    for file in sorted(os.listdir(imagePath)):

        # use regular expressions to be specific and flexible in defining file endings
        matchedFileTypes = re.findall(fileType,file)
        if len(matchedFileTypes) == 0 : continue # file did not match our fileType

        if file.endswith(matchedFileTypes[-1]):
            # double check that the regular expression match actually occured at the end of the file
            tiffFileList.append( os.path.join(imagePath,file))

    if len(tiffFileList) == 0 : 
        raise Exception("No files found whose ending matches '%s' in \n%s" %(fileType, imagePath))

    return tuple(tiffFileList)


def yieldTiffFileTuple(  imagePath : str , fileType : str) -> str:
    yield getTiffFileTuple( imagePath , fileType)