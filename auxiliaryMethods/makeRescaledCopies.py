import os
import tifffile
import skimage

import numpy as np

import matplotlib.pyplot as plt


if __name__ == "__main__":


    inputFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf"

    outputFolder = inputFolder + "_rescaled_for_Trailmap"

    os.makedirs(outputFolder, exist_ok=True)



    for file in sorted(os.listdir(inputFolder)): 
        
        image = tifffile.imread(os.path.join(inputFolder,file))

        #image_rescaled = skimage.transform.rescale(image, 0.1723 , anti_aliasing=True)
        image_rescaled = skimage.transform.resize(image, [303,303] , anti_aliasing=True)

        image_rescaled = image_rescaled / np.max(image_rescaled) * 6500

        image_rescaled = image_rescaled.astype(np.uint16)

        #image_rescaled *= 255 

        #image_rescaled = image_rescaled.astype(np.uint8)

        outputFileName = os.path.join(outputFolder, file)

        #import pdb; pdb.set_trace()

        tifffile.imwrite(outputFileName, image_rescaled)

        print(file)
        


    #os.path.dirname(inputFolder)

    print("done!")
