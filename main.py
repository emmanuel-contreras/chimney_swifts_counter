from pathlib import Path

import imageio

from skimage.morphology import (black_tophat, 
                                disk, 
                                remove_small_holes,
                                remove_small_objects,
                                dilation, 
                                erosion,
                                label, 
                                )
from tqdm import tqdm
from skimage.measure import regionprops

from numpy import ma
from skimage.filters import threshold_otsu, difference_of_gaussians

import matplotlib.pylab as plt
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300

import tifffile
import numpy as np

#%%

if __name__ == "__main__":
    
    # process a video or just a frame
    bool_video_input = True
    bool_show_frames = True
    
    if bool_video_input:
        path_vids = Path(r"./chimney_swifts")
        list_path_vids = list(path_vids.glob("*.mp4"))
    else: # load single image
        list_path_vids = [Path('./last_frame.tiff')]
    
    
    for path_vid in tqdm(list_path_vids[:]): # last video
        pass
        list_count = []
        
        if bool_video_input:
            vid = imageio.get_reader(path_vid, 'ffmpeg')
        else:
            vid = [tifffile.imread(path_vid)]
    
        for idx, frame in tqdm(enumerate(vid)):
            pass
            
            if bool_show_frames:
                plt.imshow(frame)
                plt.show()
    
            # remove building
            # frame_binary = frame[...,0] * frame[...,1] * frame[...,2]
            frame_binary = frame.sum(axis=2)
    
            thresh_otsu = threshold_otsu(frame_binary)
            
            im_mask = np.array(frame_binary > thresh_otsu, dtype=np.uint8).astype(bool)
            
            im_mask_inverted = np.invert(im_mask)
            # plt.imshow(im_mask_inverted)
            # plt.show()
            
            im_mask_inverted_holes = remove_small_holes(im_mask_inverted,
                                                        area_threshold=10000) 
            # plt.imshow(im_mask_inverted_holes)
            # plt.show()
            
           
            im_mask_inverted_holes_obj = remove_small_objects(im_mask_inverted_holes,
                                                              min_size=1000)
            # plt.imshow(im_mask_inverted_holes_obj)
            # plt.show()
            
            # remove building 
            im_sky = frame_binary * np.invert(im_mask_inverted_holes_obj)
            im_sky = im_sky**3
            # plt.imshow(im_sky)
            # plt.show()
            
                
            im_ero = erosion(im_sky,footprint=disk(2))
            # plt.imshow(im_ero)
            # plt.show()
            
            
            thresh_otsu = threshold_otsu(im_ero)
            mask_final = np.invert(im_ero > thresh_otsu)
            # plt.imshow(mask_final)
            # plt.show()
            
            ## label
            mask_labels = label(mask_final)
            
            props = regionprops(mask_labels)
            
            valid_rois = []
            for roi in props:
                if roi.area > 1000:
                    mask_labels[mask_labels==roi.label] = 0
                    continue
                valid_rois.append(roi)
            
            if bool_show_frames:
                plt.imshow(mask_labels>0)
                plt.show()
            
            list_count.append(len(valid_rois))
            
        plt.title(f"chimney_swifts \n{path_vid.name}")
        plt.plot(list_count)
        plt.ylabel("count")
        plt.xlabel("frame_number")
        plt.savefig("plot_of_swifts.tiff")
        plt.show()
        
        tifffile.imwrite("last_frame_.tiff",frame)
        tifffile.imwrite("last_mask_.tiff", mask_labels>0)
        
        np.save(f"{path_vid.stem}.npy", np.array(list_count))
    
