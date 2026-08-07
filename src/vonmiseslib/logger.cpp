/*
 * Copyright (c) 2024 Saud Zahir
 *
 * This file is part of vonMises.
 *
 * vonMises is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License.
 *
 * vonMises is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT
 * License for more details.
 */

#ifdef USE_PYTHON_LOGGING
    #include <Python.h>
#else
    #include <iostream>
#endif

#include <stdexcept>

#ifdef USE_OPENMP
    #include <omp.h>
#else
    #include <ctime>
#endif

#include "logger.h"

namespace Logger {
    LogLevel logLevel = LogLevel::DEBUG;
}

namespace {
    int PythonLevel(const Logger::LogLevel type) {
        switch (type) {
            case Logger::LogLevel::TRACE:   return 5;
            case Logger::LogLevel::DEBUG:   return 10;
            case Logger::LogLevel::INFO:    return 20;
            case Logger::LogLevel::WARNING: return 30;
            case Logger::LogLevel::ERROR:   return 40;
        }
        return 10;
    }
}

#ifdef USE_PYTHON_LOGGING

void Logger::LogMessage(
    const Logger::LogLevel type,
    const std::string& msg,
    const char* file,
    const int line
) {
    static PyObject* module = NULL;

    if (!Py_IsInitialized()) {
        Py_Initialize();
    }

    PyGILState_STATE gilState = PyGILState_Ensure();

    if (module == NULL) {
        module = PyImport_ImportModule("vonmises.logger");
        if (module == NULL) {
            PyErr_Clear();
            PyGILState_Release(gilState);
            std::fputs((msg + "\n").c_str(), stderr);
            return;
        }
    }

    PyObject* result = PyObject_CallMethod(
        module, "makeCppRecord", "issi", PythonLevel(type), msg.c_str(), file, line
    );

    if (result == NULL) {
        PyErr_Clear();
        std::fputs((msg + "\n").c_str(), stderr);
    } else {
        Py_DECREF(result);
    }

    PyGILState_Release(gilState);
}

#else

void Logger::LogMessage(
    const Logger::LogLevel type,
    const std::string& msg,
    const char* file,
    const int line
) {
    if (type <= Logger::logLevel) {
        std::cout << file << ":" << line << " - " << msg << std::endl;
    }
}

#endif

void Logger::LogAndThrowError(
    const std::string& msg, const char* file, const int line
) {
    CRITICAL_OUTPUT Logger::LogMessage(
        Logger::LogLevel::ERROR, msg, file, line
    );
    throw std::runtime_error(msg);
}

double Logger::Time() {
    #ifdef USE_OPENMP
        return omp_get_wtime();
    #else
        return static_cast<double>(clock());
    #endif
}

std::string Logger::DeltaTime(const double startTime) {
    #ifdef USE_OPENMP
        return fmt::format("{:e}s", omp_get_wtime() - startTime);
    #else
        return fmt::format("{:e}s", (clock() - startTime) / CLOCKS_PER_SEC);
    #endif
}
