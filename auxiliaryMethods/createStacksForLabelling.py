import tifffile

import os

import numpy as np

#from collections import defaultdict



def writeOutSubVolume( fullArray, sliceTuple, outputFileName):

    subVolumeVector = fullArray[sliceTuple[0],  sliceTuple[1], sliceTuple[2] ]

    #import pdb; pdb.set_trace()

    tifffile.imwrite(outputFileName, subVolumeVector)

    return None


if __name__ == "__main__":


    configListDict = []


    imageFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf"

    imageFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_pfc"

    imageFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_pvt"

    imageFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_visctx"

    imageFolder = os.path.abspath( imageFolder )

    desiredFileEnding = ".tiff"

    folderContent = sorted( [file for file in os.listdir(imageFolder) if file.endswith(desiredFileEnding)])


    imagePath = os.path.join(imageFolder,folderContent[0])

    lenX , lenY = np.shape(tifffile.imread(imagePath))
    lenZ = len(folderContent)

    print( "Image %s \nDimensions %i x %i x %i" %(imageFolder, lenX , lenY, lenZ ))

    targetArray = np.zeros([lenX, lenY, lenZ], dtype = np.uint16  )

    for zIndex , imageName in enumerate(folderContent):

        imagePath = os.path.join(imageFolder,imageName)

        xyArray = tifffile.imread(imagePath)

        targetArray[:,:,zIndex] = xyArray

        if zIndex == 100: break


    startX = 0; dX = 100
    startY = 0; dY = 100
    startZ = 0; dZ = 100

    sliceTuple = tuple( [slice(startX,dX), slice(startY,dY), slice(startZ,dZ)] )



    outputFileName = "./test.tiff"

    writeOutSubVolume( targetArray, sliceTuple, outputFileName)




    import pdb; pdb.set_trace()