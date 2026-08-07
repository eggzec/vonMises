cmake_minimum_required(VERSION 3.22...3.28)
project(vonMises)

set(CMAKE_CXX_STANDARD 11)

if(SKBUILD)
  message(STATUS "The project is built using scikit-build")
endif()

# Find and configure OpenMP
find_package(OpenMP REQUIRED)

if(OpenMP_CXX_FOUND)
    message(STATUS "OpenMP found and enabled")
    add_definitions(-DUSE_OPENMP)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

# Route C++ log records into Python's logging module. Requires the Python
# development headers; turn OFF to fall back to plain stdout logging.
option(USE_PYTHON_LOGGING "Send C++ log records to the Python logging module" ON)

if(USE_PYTHON_LOGGING)
    # Only Python.h is needed on Linux and macOS, where the symbols resolve
    # from the interpreter that dlopens the library. cibuildwheel's
    # manylinux images do not always satisfy Development.Module, so fall
    # back to the include directory scikit-build passes in, and to plain
    # stdout logging if neither is available.
    find_package(Python3 QUIET COMPONENTS Development.Module)

    if(NOT Python3_FOUND)
        if(DEFINED Python3_INCLUDE_DIR AND EXISTS "${Python3_INCLUDE_DIR}/Python.h")
            set(Python3_INCLUDE_DIRS "${Python3_INCLUDE_DIR}")
        elseif(DEFINED PYTHON_INCLUDE_DIR AND EXISTS "${PYTHON_INCLUDE_DIR}/Python.h")
            set(Python3_INCLUDE_DIRS "${PYTHON_INCLUDE_DIR}")
        else()
            message(WARNING
                "Python development headers not found; logging falls back to stdout")
            set(USE_PYTHON_LOGGING OFF)
        endif()
    endif()

    if(USE_PYTHON_LOGGING)
        message(STATUS "Python logging enabled")
    endif()
endif()

set(SOURCES
    src/vonmiseslib/vonMises_API.cpp
    src/vonmiseslib/logger.cpp
    src/vonmiseslib/rayleigh_quotient.cpp
    src/vonmiseslib/utils.cpp
    src/vonmiseslib/von_mises.cpp
)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/src/vonmises/lib)

include_directories(src/vonmises/lib)

# Add subdirectory for third-party libraries
add_subdirectory(src/vonmiseslib/thirdParty)

# Include directories for Eigen and fmt
include_directories(src/vonmiseslib/thirdParty/Eigen_3.4.0)
include_directories(src/vonmiseslib/thirdParty/fmt-10.2.1/include)

configure_file(
  "${PROJECT_SOURCE_DIR}/src/vonmiseslib/version.h.in"
  "${PROJECT_SOURCE_DIR}/src/vonmiseslib/version.h"
)

# Add shared library target for your main project
add_library(vonmises SHARED ${SOURCES})

# MSVC omits the "lib" prefix that MinGW and the Unix toolchains add, so
# pin it and keep one library name across every platform.
set_target_properties(vonmises PROPERTIES PREFIX "lib")

# Link the fmt static library with your vonmises shared library
target_link_libraries(vonmises PRIVATE fmt)

# Python logging backend
if(USE_PYTHON_LOGGING)
    target_compile_definitions(vonmises PRIVATE USE_PYTHON_LOGGING)
    target_include_directories(vonmises PRIVATE ${Python3_INCLUDE_DIRS})
    # Link against the Python ABI on Windows only: on Linux and macOS the
    # extension resolves these symbols from the interpreter that loads it,
    # and linking libpython there breaks manylinux-style distribution.
    if(WIN32)
        target_link_libraries(vonmises PRIVATE Python3::Module)
    endif()
endif()

# Link OpenMP if found
if(OpenMP_CXX_FOUND)
    target_link_libraries(vonmises PRIVATE OpenMP::OpenMP_CXX)
endif()

# Install the vonmises library
install(TARGETS vonmises LIBRARY DESTINATION lib)
