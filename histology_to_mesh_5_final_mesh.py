'''
Part 5. Mesh from registered contours' SDF
'''
import os
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

    # make sdf volume
    nimg_registered = img_registered == 0
    pos_registered = distance_transform_edt(img_registered)
    neg_registered = distance_transform_edt(nimg_registered)
    res_registered = pos_registered - neg_registered

    # smooth a bit
    return gaussian(res_registered, sigma=2)

def make_mesh(sdf, voxdim):
    '''make the final mesh'''
    v_registered, f_registered, _, _ = measure.marching_cubes(
        sdf, 0, spacing=voxdim,
        gradient_direction="ascent")

    # decimate the mesh
    success, verts, f_1, _, _ = igl.decimate(v_registered, f_registered, 20000)
    print("decimation success:", success)

    # make the mesh delaunay
    edge_lengths = igl.edge_lengths(verts, f_1)
    _, tris = igl.intrinsic_delaunay_triangulation(edge_lengths, f_1)

    return verts, tris

def make_final_mesh(
        voxdim=None,
        destination=None,
        overwrite=False):
    '''make final mesh'''

    dst = os.path.join(destination, "9_final_mesh.ply")
    if not overwrite and os.path.exists(dst):
        print('''Skipping. There is a previously computed final \
mesh (set overwrite=True to compute it again).''')
        return
    print("Computing the final mesh")

    sdf = make_sdf(destination)
    if len(sdf.shape) == 4:
        sdf = sdf[:,:,:,0]
    verts, tris = make_mesh(sdf, voxdim)
    igl.write_triangle_mesh(dst, verts, tris, force_ascii=False)
