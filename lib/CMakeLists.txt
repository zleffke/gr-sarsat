# Copyright 2011,2012,2016 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIRS})

list(APPEND sarsat_sources
)

set(sarsat_sources "${sarsat_sources}" PARENT_SCOPE)
if(NOT sarsat_sources)
	MESSAGE(STATUS "No C++ sources... skipping lib/")
	return()
endif(NOT sarsat_sources)

add_library(gnuradio-sarsat SHARED ${sarsat_sources})
target_link_libraries(gnuradio-sarsat ${Boost_LIBRARIES} ${GNURADIO_ALL_LIBRARIES})
set_target_properties(gnuradio-sarsat PROPERTIES DEFINE_SYMBOL "gnuradio_sarsat_EXPORTS")

if(APPLE)
    set_target_properties(gnuradio-sarsat PROPERTIES
        INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib"
    )
endif(APPLE)

########################################################################
# Install built library files
########################################################################
include(GrMiscUtils)
GR_LIBRARY_FOO(gnuradio-sarsat RUNTIME_COMPONENT "sarsat_runtime" DEVEL_COMPONENT "sarsat_devel")

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

include_directories(${CPPUNIT_INCLUDE_DIRS})

list(APPEND test_sarsat_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/test_sarsat.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/qa_sarsat.cc
)

add_executable(test-sarsat ${test_sarsat_sources})

target_link_libraries(
  test-sarsat
  ${GNURADIO_RUNTIME_LIBRARIES}
  ${Boost_LIBRARIES}
  ${CPPUNIT_LIBRARIES}
  gnuradio-sarsat
)

GR_ADD_TEST(test_sarsat test-sarsat)

########################################################################
# Print summary
########################################################################
message(STATUS "Using install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "Building for version: ${VERSION} / ${LIBVER}")

