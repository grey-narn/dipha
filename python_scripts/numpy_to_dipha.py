#!/usr/bin/env python3

import numpy as np
import os.path
import math
import argh


def save_numpy_array_in_dipha_format(array, dipha_fname, type_to_save=np.float64, negate=False):
    if os.path.exists(dipha_fname):
        print("File exists, skipping ", dipha_fname)
        return
    else:
        print(h5_fname, " -> ", dipha_fname)


    DIPHA_MAGIC=np.array([8067171840], dtype=np.int64)
    DIPHA_IMAGE_DATA=np.array([1], dtype=np.int64)
    n_values = np.array([array.size], dtype=np.int64)
    dim = np.array([len(array.shape)], dtype=np.int64)
    resolution = np.array(array.shape, dtype=np.int64)

    if negate:
        array = -array
    array = array.astype(type_to_save)
    array_f = np.asfortranarray(array)

    with open(dipha_fname, 'wb') as f:
        # header
        f.write(DIPHA_MAGIC)
        f.write(DIPHA_IMAGE_DATA)
        f.write(n_values.tobytes())
        f.write(dim.tobytes())
        f.write(resolution)
        # data in Fortran order
        f.write(array_f.tobytes(order='F'))



def dipha_fname_from_h5_fname(h5_fname, fields, negate, type_to_save):
    dipha_fname = h5_fname[:-5] + "_" + fields

    if type_to_save == np.float32:
        dipha_fname += ".f32"
    else:
        assert type_to_save == np.float64
        dipha_fname += ".f64"

    if negate:
         dipha_fname += ".us.dipha"
    else:
        dipha_fname += ".ls.dipha"

    dipha_fname = os.path.basename(dipha_fname)
    dipha_fname = os.path.join("$SCRATCH/striped_dataset/ldrd_cosmology/", dipha_fname)
    dipha_fname = os.path.expandvars(dipha_fname)
    return dipha_fname


if __name__ == "__main__":
    for fields in ["baryon_density", "baryon_density_dark_matter_density"]:
        for type_to_save in [np.float32, np.float64]:
            with open('hdf5_files_list_all.txt', 'r') as ff:
                for line in ff:
                    h5_fname = line.rstrip()
                    cosmology = omegas_from_fname(h5_fname)
                    data = read_fields(h5_fname, fields, cosmology)
                    data = data.astype(type_to_save)
                    save_npy(data, h5_fname, fields, type_to_save)
                    for negate in [True, False]:
                        save_dipha(data, h5_fname, negate, type_to_save)
