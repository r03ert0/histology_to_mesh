'''
Part 4. SDF volume from registered contours
'''
import os
import numpy as np
from skimage.draw import polygon, polygon_perimeter
import nibabel as nib

def load_registered_contours(destination):
    '''load registered contours from file'''
    path = os.path.join(destination, "7_registered_contours.npz")
    return np.load(
        path,
        allow_pickle=True)["registered_contours"].tolist()

def combine_contours(registered_contours):
    '''combine vertices and edges of several contours'''
    verts_registered = []
    eds_registered = []
    num_eds_registered = 0
    for i, regions in enumerate(registered_contours):
        for region in regions:
            verts_registered.extend([x, y, i] for x, y in region)
            eds_registered.extend(
                [(num_eds_registered+i,
                  num_eds_registered+(i+1)%len(region)) for i in range(len(region))])
            num_eds_registered = len(eds_registered)
    verts_registered = np.array(verts_registered)
    eds_registered = np.array(eds_registered)

    return verts_registered, eds_registered

def get_volume_min_max(verts_registered):
    '''Get volume size'''
    vmin_registered, vmax_registered = (
        np.min(verts_registered, axis=0),
        np.max(verts_registered, axis=0))
    vmin_registered = np.floor(vmin_registered)
    vmax_registered = np.ceil(vmax_registered)

    return vmin_registered, vmax_registered

def compute_mask(registered_contours, voxdim, vmin_registered, vmax_registered, offset=2):
    '''make a nifti volume with a brain mask'''
    size = vmax_registered - vmin_registered
    size[2] = len(registered_contours)
    img_registered = np.zeros([int(x) + 2*offset for x in size], 'uint8')
    print("volume shape:", img_registered.shape)
    for slce in range(len(registered_contours)):
        regions = registered_contours[slce]
        for region in regions:
            rows, cols = polygon(
                region[:, 0] - vmin_registered[0],
                region[:, 1] - vmin_registered[1],
                img_registered.shape)
            img_registered[rows+offset, cols+offset, slce+offset] = 255
            rows, cols = polygon_perimeter(
                region[:, 0] - vmin_registered[0],
                region[:, 1] - vmin_registered[1],
                img_registered.shape)
            img_registered[rows+offset, cols+offset, slce+offset] = 0
    affine = np.eye(4)
    affine[0, 0] = voxdim[0]
    affine[1, 1] = voxdim[1]
    affine[2, 2] = voxdim[2]

    return nib.Nifti1Image(img_registered, affine=affine)

def compute_final_mask(
        voxdim=None,
        destination=None,
        overwrite=False):
    '''compute the final sdf from the registered contours'''

    dst = os.path.join(destination, "8_final_mask.nii.gz")
    if not overwrite and os.path.exists(dst):
        print('''Skipping. There is a previously computed final \
mask (set overwrite=True to compute it again).''')
        return
    print("Computing the final mask")

    registered_contours = load_registered_contours(destination)
    verts_registered, _ = combine_contours(registered_contours)
    vmin_registered, vmax_registered = get_volume_min_max(verts_registered)
    mask = compute_mask(registered_contours, voxdim, vmin_registered, vmax_registered)
    nib.save(mask, dst)
