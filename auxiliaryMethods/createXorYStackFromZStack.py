import numpy as np
import tifffile
import os
import time

from tiffStackArray import tiffStackArray


def save2dArraytoTiff(image, outputPath):


    tifffile.imwrite(outputPath, image, compression ="zlib")

    print(os.path.basename(outputPath) + " saved")

    return None


if __name__ == "__main__":

    startTime = time.time()

    # load the zStack
    #zStack = tiffStackArray("/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaledForTrailmap")

    #inputFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaled_by_0.389"

    inputFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Autofluorescence-MOAB_4x/561nm_MOAB"


    zStack = tiffStackArray(inputFolder)


    print("Loaded zStack in %.2f" %(time.time()-startTime) )

    #zyxSelection = (slice(None),slice(1800,2800+1),slice(None))
    #zyxSelection = (slice(None),slice(None),slice(2350,3100+1)) # rescaled DBH images
    zyxSelection = (slice(None),slice(None),slice(2200,3200+1)) # try this for autofluorescense and MOAB
    #zyxSelection = (slice(1000,1100),slice(None),slice(2350,3100+1))

    XorYSlice = None
    yxIndex = None

    
    if zyxSelection[1] == slice(None):
        XorYSlice = "x"
        yxIndex = 2

    elif zyxSelection[2] == slice(None):
        XorYSlice = "y"
        yxIndex = 1
    
    if XorYSlice is None: 
        raise ValueError("This function only works for x or y slices")

    # scale the imageArray3d to 8bit
    imageArray3d = zStack[zyxSelection].astype(np.float32)
    imageArray3d = (imageArray3d - np.min(imageArray3d)) / (np.max(imageArray3d) - np.min(imageArray3d)) * 255
    imageArray3d = np.round(imageArray3d).astype(np.uint8)

    outputFolder = inputFolder+"_8bit_%sSlices_%i_to_%i" %(XorYSlice,zyxSelection[yxIndex].start, zyxSelection[yxIndex].stop-1)
    os.makedirs(outputFolder, exist_ok=True)

    print("Transformed zStack in %.2f" %(time.time()-startTime) )

    for index in range(imageArray3d.shape[yxIndex]):



        outputPath = os.path.join(outputFolder, "%sSlice_%i.tif" % (XorYSlice, index+zyxSelection[yxIndex].start))

        #import pdb; pdb.set_trace()

        localSliceTuple = [slice(None),slice(None),slice(None)]
        localSliceTuple[yxIndex] = slice(index,index+1)

        save2dArraytoTiff(imageArray3d[tuple(localSliceTuple)], outputPath)

    print("Elapsed time: %.2f" %(time.time()-startTime))
