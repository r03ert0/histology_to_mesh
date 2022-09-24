'''histology_to_mesh.py'''

import sys
import os
import histology_to_mesh_1_download as io
import histology_to_mesh_2_intermediate_mesh as mesh
import histology_to_mesh_3_register as register
import histology_to_mesh_4_sdf as sdf
import histology_to_mesh_5_final_mesh as final

def histology_to_mesh(
    project=None,
    source=None,
    token=None,
    regions=None,
    voxdim=None,
    destination=None,
    overwrite=False
):
    '''
    3D mesh reconstruction from Microdraw segmentation
    '''

    destination = os.path.expanduser(destination)
    destination = os.path.abspath(destination)

    print(f"    project: {project}")
    print(f"     source: {source}")
    print(f"      token: {token}")
    print(f"    regions: {regions}")
    print(f"     voxdim: {voxdim}")
    print(f"destination: {destination}")
    print(f"  overwrite: {overwrite}")

    io.download_from_microdraw_and_save(
        project=project,
        source=source,
        token=token,
        destination=destination,
        overwrite=overwrite
    )

    mesh.make_intermediate_mesh(
        regions=regions,
        voxdim=voxdim,
        destination=destination,
        overwrite=overwrite
    )

    register.register_contours(
        voxdim=voxdim,
        destination=destination,
        overwrite=overwrite)
    
    sdf.compute_final_mask(
        voxdim=voxdim,
        destination=destination,
        overwrite=overwrite
    )

    final.make_final_mesh(
        voxdim=voxdim,
        destination=destination,
        overwrite=overwrite
    )

def main(argv):
  '''convenience histology_to_mesh call from the command line'''
  _, project, source, token, regions, voxdim, destination, overwrite = argv

  regions = regions.split(",")
  voxdim = [float(s) for s in voxdim.split(",")]
  overwrite = overwrite=="True"

  histology_to_mesh(project, source, token, regions,
    voxdim, destination, overwrite)

# if __name__ == "__main__":
#   main(sys.argv)

# histology_to_mesh(
#   project="FIIND",
#   source="https://microdraw.pasteur.fr/F107_P4_Nissl_x20/F107_P4.json",
#   token="",
#   regions=["Region 1", "Region 2"],
#   voxdim=[0.1, 0.1, 1.25],
#   destination="/Users/roberto/Desktop/out",
#   overwrite=False)

# python histology_to_mesh.py FIIND https://microdraw.pasteur.fr/F107_P4_Nissl_x20/F107_P4.json "" "Region 1","Region 2" 0.1,0.1,1.25 ~/Desktop/out/ False

# histology_to_mesh(
#   project="FIINDgw",
#   source="https://microdraw.pasteur.fr/F107_P4_Nissl_x20/F107_P4.json",
#   token="",
#   regions=["Region 1", "Region 2"],
#   voxdim=[0.1, 0.1, 1.25],
#   destination="~/Desktop/p4-gw/",
#   overwrite=True)

# histology_to_mesh(
#   project="FIINDnctx",
#   source="https://microdraw.pasteur.fr/F107_P4_Nissl_x20/F107_P4.json",
#   token="",
#   regions=["Region 1", "Region 2"],
#   voxdim=[0.1, 0.1, 1.25],
#   destination="~/Desktop/p4-nctx/",
#   overwrite=True)

histology_to_mesh(
  project="FIINDgw",
  source="https://microdraw.pasteur.fr/F110_P8_Nissl_x20/F110_P8.json",
  token="",
  regions=["Region 1", "Region 2"],
  voxdim=[0.1, 0.1, 2],
  destination="~/Desktop/p8-gw/",
  overwrite=True)

# histology_to_mesh(
#   project="FIINDnctx",
#   source="https://microdraw.pasteur.fr/F110_P8_Nissl_x20/F110_P8.json",
#   token="",
#   regions=["Region 1", "Region 2"],
#   voxdim=[0.1, 0.1, 2],
#   destination="~/Desktop/p8-nctx/",
#   overwrite=False)