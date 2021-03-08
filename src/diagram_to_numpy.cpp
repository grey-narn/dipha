#include <fstream>
#include <iostream>
#include <vector>
#include <cmath>
#include <unordered_map>
#include <utility>

#include <cnpy/cnpy.h>

#include "dipha/includes.h"

using namespace dipha;

using FlattenedDgm = std::vector<dipha_real>;


int main(int argc, char** argv)
{
    if (argc != 3 && argc != 2) {
        std::cerr << "Usage: " << argv[0] << " dipha-diagram [out-diagram]" << std::endl;
        return -1;
    }

    std::string dgm_in = argv[1];
    std::string dgm_out = (argc == 3) ? argv[2] : dgm_in;

    std::ifstream in(dgm_in, std::ios::binary);

    if (!in.good()) {
        std::cerr << "cannot open " << dgm_in << std::endl;
        return -1;
    }

    int64_t preamble_magic;
    int64_t preamble_file_type;
    int64_t n_pairs;

    in.read(reinterpret_cast<char*>(&preamble_magic), sizeof(int64_t));

    if (preamble_magic != file_types::DIPHA) {
        std::cerr << "Dipha files must start with " << file_types::DIPHA <<", read: " << preamble_magic << std::endl;
        return -1;
    }

    in.read(reinterpret_cast<char*>(&preamble_file_type), sizeof(int64_t));

    if (preamble_file_type != file_types::PERSISTENCE_DIAGRAM) {
        std::cerr << "Wrong file type, expected " << file_types::PERSISTENCE_DIAGRAM <<", read: " << preamble_file_type << std::endl;
        return -1;
    }

    in.read(reinterpret_cast<char*>(&n_pairs), sizeof(int64_t));

    std::cout << "file contains " << n_pairs << " pairs." << std::endl;

    std::unordered_map<int64_t, FlattenedDgm> dim_to_diagram;

    constexpr dipha_real min_persistence = (sizeof(dipha_real) == sizeof(float)) ? 1e-32 : 1e-200;

    for(int64_t pair_index = 0; pair_index < n_pairs; ++pair_index) {
        int64_t dim;
        dipha_real birth, death;

        in.read(reinterpret_cast<char*>(&dim), sizeof(int64_t));
        in.read(reinterpret_cast<char*>(&birth), sizeof(dipha_real));
        in.read(reinterpret_cast<char*>(&death), sizeof(dipha_real));
        if (!(fabs(birth - death) < min_persistence)) {
            dim_to_diagram[dim].emplace_back(birth);
            dim_to_diagram[dim].emplace_back(death);
        }
    }

    for(const auto& dim_dgm : dim_to_diagram) {
        if (dim_dgm.second.size() == 0)
            continue;

        std::cout << "Saving dimension " << dim_dgm.first << ", diagram with " << dim_dgm.second.size() / 2 << " points." << std::endl;

        if (dim_dgm.second.size() % 2)
            throw std::runtime_error("Flattened diagram must have even size");

        std::string dgm_fname = dgm_out + "." + std::to_string(dim_dgm.first) + ".npy";
        const FlattenedDgm& dgm = dim_dgm.second;
        cnpy::npy_save(dgm_fname, &dgm[0], {dgm.size() / 2, 2}, "w");
    }

    return 0;
}
