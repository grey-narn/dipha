#!/usr/bin/env python3

import h5py
import numpy as np
import os.path
import math

class CosmolodyParams:
    pass

# G = 6.673e-8
# pi =math.pi
# rho_c_units_conversion = 1.0e10 * 3.08568025e24 * 5.02785431e-34

# rho_c = (3e4*hubble**2 / (8 * pi * G)) * rho_c_units_conversion


# as in README in /global/projects/projectdirs/nyx/www/thermal
def omegas_from_fname(fname):
    result = CosmolodyParams()
    if fname.find('C009') > 0:
        result.omega_b =0.049648
        result.omega_m=0.319181
        result.hubble=0.670386
    elif fname.find('C000') > 0:
        result.omega_b =0.046
        result.omega_m=0.275
        result.hubble=0.702
    elif fname.find('C002') > 0:
        result.omega_b = 0.047711
        result.omega_m = 0.298470
        result.hubble = 0.686450
    elif fname.find('C015') > 0:
        result.omega_b = 0.051684
        result.omega_m = 0.333446
        result.hubble = 0.657788
    print(f"Read {(result.omega_b, result.omega_m, result.hubble)}")
    return result


def save_dipha(array, h5_fname, negate, type_to_save=np.float64):
    dipha_fname = dipha_fname_from_h5_fname(h5_fname, fields, negate, type_to_save)
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


def save_npy(array, h5_fname, fields, type_to_save):
    npy_fname = npy_fname_from_h5_fname(h5_fname, fields, type_to_save)
    if not os.path.exists(npy_fname):
        print(h5_fname, " -> ", npy_fname)
        np.save(npy_fname, data)
    else:
        print("File exists, skipping ", npy_fname)


def read_fields(h5_fname, fields, cosmology):
    assert fields in ["baryon_density", "dark_matter_density", "baryon_density_dark_matter_density"]
    with h5py.File(h5_fname, 'r') as f:
        if fields in ["baryon_density", "dark_matter_density"]:
            data = f.get(f"/native_fields/{fields}").value
        elif fields in ["baryon_density_dark_matter_density"]:
            # need to rescale, Zarija's email from Wed, Jul 22, 2:15 AM
            data_dmd = f.get(f"/native_fields/dark_matter_density").value
            data_bd = f.get(f"/native_fields/baryon_density").value
            data = (cosmology.omega_m - cosmology.omega_b) * data_dmd + cosmology.omega_b * data_bd
            del data_dmd, data_bd
    return data


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


def npy_fname_from_h5_fname(h5_fname, fields, type_to_save):
    npy_fname = h5_fname[:-5] + "_" + fields
    if type_to_save == np.float32:
        npy_fname += ".f32.npy"
    else:
        assert type_to_save == np.float64
        npy_fname += ".f64.npy"
    npy_fname = os.path.basename(npy_fname)
    npy_fname = os.path.join("$SCRATCH/striped_dataset/ldrd_cosmology/", npy_fname)
    npy_fname = os.path.expandvars(npy_fname)
    return npy_fname


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
