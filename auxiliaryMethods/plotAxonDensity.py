from tiffStackArray import tiffStackArray

import numpy as np
import matplotlib.pyplot as plt

import os


if __name__ == "__main__":

    figureTargetFolder = "/home/chweber/ssd1_chweber/temp"

    axonSegmentationPath = "/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/DBH_hpf_TrailmapHistMatched_rescaled_segmented"



    trailmapImageArray = tiffStackArray(axonSegmentationPath)[:]


    # plot a histogram of the trailmapImageArray
    plt.figure()  # Create a new figure
    plt.hist(trailmapImageArray.flatten(), bins=100)

    # make hte y axis logaritmic
    plt.yscale('log')

    plt.show()

    # add label to the x axis
    plt.xlabel("axon probability")
    plt.ylabel("frequency")

    plt.savefig( os.path.join(figureTargetFolder,"AxonDensityHistograms.png"))


    axonProbabilityThreshold = 0.5

    axonDensity = np.sum(trailmapImageArray > axonProbabilityThreshold) / np.prod(trailmapImageArray.shape)

    axonDensityList = [axonDensity, -1]
    plaqueDensityList = [-0.5, -2]

    

    XLabelList = ['dieased', 'wild type'] 
    X_axis = np.arange(len(XLabelList))  

    # plot a bar graph of the axon density
    plt.figure()  # Create a new figure

    plt.bar(X_axis - 0.2, axonDensityList, 0.4, label = 'Axon Density') 
    plt.bar(X_axis + 0.2, plaqueDensityList, 0.4, label = 'Plaque Density') 

    plt.xticks(X_axis, XLabelList) 

    plt.ylabel("Relative Density")


    # add a legend
    plt.legend()

    plt.savefig( os.path.join(figureTargetFolder,"AxonDensity.png"))






    pass