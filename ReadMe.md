# Histology to mesh

Converts a series of annotations from MicroDraw into a mesh.

The algorithm:

1. Downloads all data from MicroDraw. An svg is produced summarising all annotations downloaded.
2. An intermediate mesh is created by stacking all annotation together, creating a mask, and generating a mesh. The mesh is heavily smoothed to provide an estimation of the core of the annotated object.
3. The initial annotations are registered to the smoothed mesh.
4. A signed distance function is created from the annotations.
5. The SDF is used to create the final mesh.

This final mesh can be manually edited, using MeshSurgery or Model Collection, and then used instead of the intermediate mesh to restart from step 3.

`histology_to_mesh` can be used from a Python script like this:

```python
import histology_to_mesh as h2m

h2m.histology_to_mesh(
  project="FIINDgw",
  source="https://microdraw.pasteur.fr/F107_P4_Nissl_x20/F107_P4.json",
  token="",
  regions=["Region 1", "Region 2"],
  voxdim=[0.1, 0.1, 1.25],
  destination="~/Desktop/out-p4-gw/",
  overwrite=True)
```

`histology_to_mesh` can be also used from the command line:

```bash
python histology_to_mesh.py \
    FIIND \
    https://microdraw.pasteur.fr/F107_P4_Nissl_x20/F107_P4.json \
    "" \
    "Region 1","Region 2" \
    0.1,0.1,1.25 \
    ~/Desktop/out/ \
    False
```

Note that there should be no spaces after the comma in the list of regions or in the list of voxel dimensions.
