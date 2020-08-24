#pragma once

namespace dipha {
#ifdef DIPHA_REAL
    using dipha_real = DIPHA_REAL;
#else
    // to raise error
    using dipha_real = void;
#endif
}
