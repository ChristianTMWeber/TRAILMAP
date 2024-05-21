from tiffStackArray import tiffStackArray

import numpy as np
import matplotlib.pyplot as plt



if __name__ == "__main__":

    axonSegmentationPath = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf_TrailmapHistMatched_rescaled_segmented"



    trailmapImageArray = tiffStackArray(axonSegmentationPath)[:]


    # plot a histogram of the trailmapImageArray
    plt.hist(trailmapImageArray.flatten(), bins=100)
    plt.show()



    plt.savefig("histograms.png")



    pass