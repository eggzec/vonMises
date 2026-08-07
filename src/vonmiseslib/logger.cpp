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

#ifdef USE_PYTHON_LOGGING

/*
 * Route C++ messages into Python's `logging` module so that library output
 * and application output share one stream, one format and one level.
 *
 * Levels are offset by +1 from the Python constants (and TRACE is 5) so
 * that C++ records remain distinguishable from Python ones; the names are
 * registered in vonmises/logger.py as c:DEBUG, c:INFO and so on.
 *
 * Adapted from https://gist.github.com/hensing/0db3f8e3a99590006368
 */
void Logger::LogMessage(const Logger::LogLevel type, const std::string& msg) {
    static PyObject* logging = NULL;
    static PyObject* logger = NULL;

    // The library may be loaded outside a running interpreter (for example
    // by the standalone executable), so make sure Python is initialised.
    if (!Py_IsInitialized()) {
        Py_Initialize();
    }

    // Any thread reaching this point must hold the GIL before touching the
    // CPython API; OpenMP worker threads do not hold it by default.
    PyGILState_STATE gilState = PyGILState_Ensure();

    if (logging == NULL) {
        logging = PyImport_ImportModule("logging");
        if (logging == NULL) {
            PyErr_Clear();
            PyGILState_Release(gilState);
            std::fputs((msg + "\n").c_str(), stderr);
            return;
        }
    }

    if (logger == NULL) {
        logger = PyObject_CallMethod(logging, "getLogger", "s", "vonMises");
        if (logger == NULL) {
            PyErr_Clear();
            PyGILState_Release(gilState);
            std::fputs((msg + "\n").c_str(), stderr);
            return;
        }
    }

    int level = 11;
    switch (type) {
        case Logger::LogLevel::TRACE:   level = 5;  break;  // custom c:TRACE
        case Logger::LogLevel::DEBUG:   level = 11; break;  // logging.DEBUG + 1
        case Logger::LogLevel::INFO:    level = 21; break;  // logging.INFO + 1
        case Logger::LogLevel::WARNING: level = 31; break;  // logging.WARNING + 1
        case Logger::LogLevel::ERROR:   level = 41; break;  // logging.ERROR + 1
    }

    PyObject* result = PyObject_CallMethod(logger, "log", "is", level, msg.c_str());
    if (result == NULL) {
        PyErr_Clear();
    } else {
        Py_DECREF(result);
    }

    PyGILState_Release(gilState);
}

#else

void Logger::LogMessage(const Logger::LogLevel type, const std::string& msg) {
    if (type <= Logger::logLevel) {
        std::cout << msg << std::endl;
    }
}

#endif

void Logger::LogAndThrowError(const std::string& msg) {
    CRITICAL_OUTPUT Logger::LogMessage(Logger::LogLevel::ERROR, msg);
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
