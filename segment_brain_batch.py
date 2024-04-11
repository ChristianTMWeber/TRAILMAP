from inference import *
from models import *
import sys
import os
import shutil
import argparse # to parse command line options


def initilizeArgParser( parser = argparse.ArgumentParser(
    description="") ):

    parser.add_argument("foldersToSegment", type=str,nargs='*',
        help="List of folders that we want to segment" )

    parser.add_argument("-o","--outputFolders", type=str, nargs='*', required = False , 
        help="Folder where we store the segmentation map \
        This is an optional argument.\
        If this argument is not provided, we will output the each segmentation map to \
        <path_to_n-th_input>\\seg-<top_level_n-th_input>.")

    parser.add_argument( "--dryRun", default=False, action= 'store_true' ,
    help = "With this option we skip the step of actually segmenting the images, \
    and only list the inputs that we would process and where the outputs would go." )

    args = parser.parse_args()


    if args.outputFolders is not None:
        assert len(args.foldersToSegment) == len(args.outputFolders), \
        "should have same number of input folders as output folders"

    return args


if __name__ == "__main__":

    args = initilizeArgParser()

    base_path = os.path.abspath(__file__ + "/..")

    #input_batch = sys.argv[1:]
    ## Verify each path is a directory
    #for input_folder in input_batch:
    #    if not os.path.isdir(input_folder):
    #        raise Exception(input_folder + " is not a directory. Inputs must be a folder of files. Please refer to readme for more info")

    # Load the network
    weights_path = base_path + "/data/model-weights/trailmap_model.hdf5"

    model = get_net()
    model.load_weights(weights_path)

    for folderIndex , input_folder in enumerate(args.foldersToSegment):

        #import pdb; pdb.set_trace() # import the debugger and instruct it to stop here

        input_folder = os.path.realpath(input_folder)

        assert os.path.isdir(input_folder)

        # Remove trailing slashes
        input_folder = os.path.normpath(input_folder)

        # Output folder name

        if args.outputFolders is None:
            output_name = "seg-" + os.path.basename(input_folder)
            output_dir = os.path.dirname(input_folder)
            output_folder = os.path.join(output_dir, output_name)

        else:

            output_folder = os.path.realpath( args.outputFolders[folderIndex] )

        #print( "\n\n\nUSING TEMP OUTPUT FOLDER\n\n\n")
        #output_folder="/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/Chung_59405_9x-1umZstep_RightHemi_DBH/647nm_DBH_segmentation"


        # Create output directory. Overwrite if the directory exists
        if os.path.exists(output_folder):
            print(output_folder + " already exists. Will be overwritten")
            shutil.rmtree(output_folder)

        os.makedirs(output_folder)

        # Segment the brain
        segment_brain(input_folder, output_folder, model)

