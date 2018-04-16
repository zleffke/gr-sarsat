INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_SARSAT sarsat)

FIND_PATH(
    SARSAT_INCLUDE_DIRS
    NAMES sarsat/api.h
    HINTS $ENV{SARSAT_DIR}/include
        ${PC_SARSAT_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SARSAT_LIBRARIES
    NAMES gnuradio-sarsat
    HINTS $ENV{SARSAT_DIR}/lib
        ${PC_SARSAT_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SARSAT DEFAULT_MSG SARSAT_LIBRARIES SARSAT_INCLUDE_DIRS)
MARK_AS_ADVANCED(SARSAT_LIBRARIES SARSAT_INCLUDE_DIRS)

