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
    # from the interpreter that dlopens the library. Windows additionally
    # needs the import library. cibuildwheel images do not always satisfy
    # Development.Module, so fall back to the paths scikit-build passes in,
    # and to plain stdout logging if neither is available.
    find_package(Python3 QUIET COMPONENTS Development.Module)

    if(Python3_FOUND)
        set(VONMISES_PY_INCLUDE "${Python3_INCLUDE_DIRS}")
    elseif(DEFINED Python3_INCLUDE_DIR AND EXISTS "${Python3_INCLUDE_DIR}/Python.h")
        set(VONMISES_PY_INCLUDE "${Python3_INCLUDE_DIR}")
    elseif(DEFINED PYTHON_INCLUDE_DIR AND EXISTS "${PYTHON_INCLUDE_DIR}/Python.h")
        set(VONMISES_PY_INCLUDE "${PYTHON_INCLUDE_DIR}")
    else()
        set(USE_PYTHON_LOGGING OFF)
    endif()

    if(USE_PYTHON_LOGGING AND WIN32)
        if(TARGET Python3::Module)
            set(VONMISES_PY_LIB Python3::Module)
        elseif(DEFINED Python3_LIBRARY AND EXISTS "${Python3_LIBRARY}")
            set(VONMISES_PY_LIB "${Python3_LIBRARY}")
        elseif(DEFINED PYTHON_LIBRARY AND EXISTS "${PYTHON_LIBRARY}")
            set(VONMISES_PY_LIB "${PYTHON_LIBRARY}")
        else()
            set(USE_PYTHON_LOGGING OFF)
        endif()
    endif()

    if(USE_PYTHON_LOGGING)
        message(STATUS "Python logging enabled")
    else()
        message(WARNING
            "Python development files not found; logging falls back to stdout")
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
    target_include_directories(vonmises PRIVATE ${VONMISES_PY_INCLUDE})

    if(WIN32)
        target_link_libraries(vonmises PRIVATE ${VONMISES_PY_LIB})
    elseif(APPLE)
        # The macOS linker resolves every symbol at link time unless told
        # otherwise, so the CPython symbols must be deferred to load time.
        # Linux already behaves this way.
        target_link_options(vonmises PRIVATE -Wl,-undefined,dynamic_lookup)
    endif()
endif()

# Link OpenMP if found
if(OpenMP_CXX_FOUND)
    target_link_libraries(vonmises PRIVATE OpenMP::OpenMP_CXX)
endif()

# Install the vonmises library
install(TARGETS vonmises LIBRARY DESTINATION lib)
