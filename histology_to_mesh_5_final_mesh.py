'''
Part 5. Mesh from registered contours' SDF
'''
import os
import numpy as np
import nibabel as nib
from scipy.ndimage import distance_transform_edt
import igl
from skimage.filters import gaussian
from skimage import measure

def make_sdf(destination):
    '''make sdf from mask'''
    path = os.path.join(destination, "8_final_mask.nii.gz")
    nii_registered = nib.load(path)
    img_registered = nii_registered.get_fdata()

    print('''@todo The mask volume is tight around the object.
    The sdf here and its smoothing could use some offset.
    ''')

    # make sdf volume
    nimg_registered = img_registered == 0
    pos_registered = distance_transform_edt(img_registered)
    neg_registered = distance_transform_edt(nimg_registered)
    res_registered = pos_registered - neg_registered

    # smooth a bit
    return gaussian(res_registered, sigma=2)

def make_mesh(sdf, voxdim, original_center, level=0):
    '''make the final mesh'''
    print("@todo: make_mesh in hm_5 is identical to compute_mesh in hm_2")
    v_registered, f_registered, _, _ = measure.marching_cubes(
        sdf, spacing=voxdim, level=level,
        gradient_direction="ascent")

    # transform to match space
    mesh_center = (np.min(v_registered, axis=0) + np.max(v_registered, axis=0))/2
    print("mesh center:", mesh_center)
    displacement = original_center - mesh_center/voxdim

    # decimate
    success, verts, f_1, _, _ = igl.decimate(v_registered, f_registered, 20000)
    print("decimation success:", success)

    # improve triangulation
    edge_lengths = igl.edge_lengths(verts, f_1)
    _, tris = igl.intrinsic_delaunay_triangulation(edge_lengths, f_1)

    return verts, tris, displacement

def make_final_mesh(
        voxdim=None,
        destination=None,
        level=0,
        overwrite=False):
    '''make final mesh'''

    dst = os.path.join(destination, "10_final_mesh.ply")
    if not overwrite and os.path.exists(dst):
        print('''Skipping. There is a previously computed final \
mesh (set overwrite=True to compute it again).''')
        return
    print("Computing the final mesh")

    sdf = make_sdf(destination)
    if len(sdf.shape) == 4:
        sdf = sdf[:,:,:,0]

    path = os.path.join(destination, "9_contours_center.npz")
    original_center = np.load(path, allow_pickle=True)["contours_center"]

    verts, tris, displacement = make_mesh(sdf, voxdim, original_center, level)
    igl.write_triangle_mesh(dst, verts, tris, force_ascii=False)
    path = os.path.join(destination, "11_displacement.npz")
    np.savez_compressed(path, displacement=displacement)

