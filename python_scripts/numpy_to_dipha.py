#!/usr/bin/env python3

import numpy as np
import os.path
import sys


def convert_np_to_dipha(np_fname, dipha_fname, type_to_save=np.float64, negate=False):
    if os.path.exists(dipha_fname):
        print("File exists, skipping ", dipha_fname)
        return
    else:
        print(np_fname, " -> ", dipha_fname)

    array = np.load(np_fname)

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


if __name__ == "__main__":
    np_fname = sys.argv[1]
    dipha_fname = sys.argv[2]
    negate = False

    convert_np_to_dipha(np_fname, dipha_fname, type_to_save=np.float64, negate=negate)

