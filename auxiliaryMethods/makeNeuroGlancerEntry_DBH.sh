#!/bin/bash



#TiffSource="/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaled_by_0.389/*.tif*"
#PrecompTiffTarget="/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaled_by_0.389_precomp"
#NeuroGlancerName="Tsai_MouseBrain57611_DBHrescale"


#TiffSource="/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaledForTrailmap/*.tif*"
#PrecompTiffTarget="/media/ssdshare1/general/chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaledForTrailmap_precomp"
#NeuroGlancerName="Tsai_MouseBrain57611_DBHrescaleForTrailmap"



TiffSource="/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaledForTrailmap_8bit_xSlices_2350_to_3100/*.tif*"
PrecompTiffTarget="/home/chweber/ssd1_chweber/U01_towards_integrated_3D_reconstruction/tsai_collab_data/UO1_appkihomo_57611/Chung-Tsai_MouseBrain57611_Lectin-DBH_9x/639nm_DBH_rescaledForTrailmap_8bit_xSlices_2350_to_3100_precomp"
NeuroGlancerName="Tsai_MouseBrain57611_DBHrescaleForTrailmap_xSlices_2350_to_3100"





### setup the necessary conda environment
source /home/build/anaconda3/bin/activate chunglab-stack
conda activate chunglab-stack

### precompute the tiffs, those precomputed tiffs will be linked against the database

time precomputed-tif --source "$TiffSource"  --dest "$PrecompTiffTarget" --format blockfs --n-cores 20 --levels 5

### link against the database
python /media/share7/add_source.py --name $NeuroGlancerName --directory $PrecompTiffTarget 

### get the neuroglancer url
/media/share7/neuroglancer_url.py $NeuroGlancerName blue 60