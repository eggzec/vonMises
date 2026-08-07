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

#ifndef VONMISES_LOGGER_H
#define VONMISES_LOGGER_H

#include <string>

#include <fmt/core.h>
#include <fmt/format.h>

namespace Logger {
    enum class LogLevel { ERROR, WARNING, INFO, DEBUG, TRACE };

    extern LogLevel logLevel;

    void LogMessage(
        const LogLevel type,
        const std::string& msg,
        const char* file,
        const int line
    );
    void LogAndThrowError(
        const std::string& msg, const char* file, const int line
    );

    double Time();
    std::string DeltaTime(const double startTime);
}

#ifdef USE_OPENMP
    #define CRITICAL_OUTPUT _Pragma("omp critical (IOSync)")
#else
    #define CRITICAL_OUTPUT
#endif

#define TRACE_OUT(s, ...)                    \
    CRITICAL_OUTPUT Logger::LogMessage(      \
        Logger::LogLevel::TRACE,             \
        fmt::format(FMT_STRING(s), ##__VA_ARGS__), __FILE__, __LINE__)
#define DEBUG_OUT(s, ...)                    \
    CRITICAL_OUTPUT Logger::LogMessage(      \
        Logger::LogLevel::DEBUG,             \
        fmt::format(FMT_STRING(s), ##__VA_ARGS__), __FILE__, __LINE__)
#define INFO_OUT(s, ...)                     \
    CRITICAL_OUTPUT Logger::LogMessage(      \
        Logger::LogLevel::INFO,              \
        fmt::format(FMT_STRING(s), ##__VA_ARGS__), __FILE__, __LINE__)
#define WARNING_OUT(s, ...)                  \
    CRITICAL_OUTPUT Logger::LogMessage(      \
        Logger::LogLevel::WARNING,           \
        fmt::format(FMT_STRING(s), ##__VA_ARGS__), __FILE__, __LINE__)
#define ERROR_OUT(s, ...)                    \
    Logger::LogAndThrowError(                \
        fmt::format(FMT_STRING(s), ##__VA_ARGS__), __FILE__, __LINE__)

inline std::string methodName(const std::string& prettyFunction) {
    size_t colons = prettyFunction.find("::");
    size_t begin = prettyFunction.substr(0, colons).rfind(" ") + 1;
    size_t end = prettyFunction.rfind("(") - begin;

    return prettyFunction.substr(begin, end) + "()";
}

#ifdef _MSC_VER
    #define __METHOD_NAME__ __FUNCSIG__
#else
    #define __METHOD_NAME__ methodName(__PRETTY_FUNCTION__)
#endif

#define FUNC_ENTER \
    TRACE_OUT("- Starting  '{}'", __METHOD_NAME__); \
    const double __function_start = Logger::Time();
#define FUNC_EXIT \
    TRACE_OUT("- Completed '{}' in {}", __METHOD_NAME__, Logger::DeltaTime(__function_start));

inline double clocktime() { return Logger::Time(); }
inline std::string deltaTime(const double startTime) { return Logger::DeltaTime(startTime); }

#endif // VONMISES_LOGGER_H
