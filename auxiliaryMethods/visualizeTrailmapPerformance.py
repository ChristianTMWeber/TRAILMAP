import numpy as np
import tifffile
import os
import time

import matplotlib.pyplot as plt
import matplotlib.patches as patches


from tiffStackArray import tiffStackArray



def getImageArrayFromFolder(imageFolder, sliceTuple = (slice(None),slice(None),slice(2350,3100+1))):

    imageStack = tiffStackArray(imageFolder)

    imageArray = imageStack[sliceTuple]

    return imageArray


def save2dArraytoTiff(image, outputPath):


    tifffile.imwrite(outputPath, image, compression ="zlib")

    print(os.path.basename(outputPath) + " saved")

    return None


if __name__ == "__main__":

    DBH_imageFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaled_by_0.389"

    MOAB_imageFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Autofluorescence-MOAB_4x/561nm_MOAB"

    segmentation_imageFolder = "/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaled_by_0.389_histMatched_segmented"


    startTime = time.time()
    DBH_Array = getImageArrayFromFolder(DBH_imageFolder)
    segmentation_Array = getImageArrayFromFolder(segmentation_imageFolder)
    MOAB_ArrayFull = getImageArrayFromFolder(MOAB_imageFolder, sliceTuple = (slice(None),slice(None),slice(2200,3200+1) ) )

    print("Loaded image arrays in %.2fs" %(time.time()-startTime) )



    saggitalSliceTuple = (slice(None),slice(None),slice(24,50))

    DBH_MIPx_projection = np.max(DBH_Array[saggitalSliceTuple], axis = 2)
    segmentation_MIPx_projection = np.max(segmentation_Array[saggitalSliceTuple], axis = 2)


    aspectRatio = DBH_MIPx_projection.shape[0]/DBH_MIPx_projection.shape[1]

    width = 900
    zoomInPatch = patches.Rectangle((1700,1300),width,int(width * aspectRatio ),linewidth=1,edgecolor='r',facecolor='none')   

    patchList = []


    x0= zoomInPatch.xy[0]
    y0 = zoomInPatch.xy[1]

    dx= zoomInPatch.get_width()
    dy= zoomInPatch.get_height()


    zoomInSliceTuple = (slice(y0,y0+dy+1),slice(x0,x0+dx+1))




    DBH_MIPx_projection_changed = DBH_MIPx_projection *40
    segmentation_MIPx_projection_changed = 1* segmentation_MIPx_projection 



    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2,dpi=600, figsize = (6.4,3.0) )

    ax1.imshow(DBH_MIPx_projection_changed, cmap = "gray")
    patchList.append(patches.Rectangle((x0,y0),dx,dy,linewidth=1,edgecolor='r',facecolor='none') )
    ax1.add_patch(patchList[-1])

    ax1.set_title("DBH stained mouse brain, saggital slice", fontsize = 7)

    ax2.imshow(DBH_MIPx_projection_changed[zoomInSliceTuple], cmap = "gray")
    ax2.set_title("Zoom in on highlighted region of saggital slice", fontsize = 7)

    ax3.imshow(segmentation_MIPx_projection_changed, cmap = "gray")
    patchList.append(patches.Rectangle((x0,y0),dx,dy,linewidth=1,edgecolor='r',facecolor='none') )
    ax3.set_title("Axon segmentation derived from DBH image", fontsize = 7)
    ax3.add_patch(patchList[-1])


    ax4.imshow(segmentation_MIPx_projection_changed[zoomInSliceTuple], cmap = "gray")
    ax4.set_title("Zoom in on highlighted axon segmentation region", fontsize = 7)
    #plt.show()


    for axes in [ax1, ax2, ax3, ax4]:
        axes.set_xticks([])
        axes.set_yticks([])

    fig.savefig("DBH_segmentation_comparison.pdf",bbox_inches='tight')
    fig.savefig("DBH_segmentation_comparison.png",bbox_inches='tight')

    plt.close()





    pass