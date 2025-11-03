/*
 * Parameter structures for 4K Softsynth
 * Shared definitions for parameter types, ranges, and enums
 */

#pragma once

#include <vector>
#include <string>
#include <cstdint>

// Parameter data types
enum class ParameterType : uint8_t
{
    UINT8 = 0,
    UINT16 = 1,
    ENUM = 2
};

// Parameter range information including step
struct ParameterRange
{
    int min_value;
    int max_value;
    int step;

    ParameterRange(int min_val, int max_val, int step_val = 1)
        : min_value(min_val), max_value(max_val), step(step_val) {}
};

// Enum parameter value mapping
struct EnumValue
{
    uint8_t value;
    std::string name;

    EnumValue(uint8_t val, const std::string &n) : value(val), name(n) {}
};

// Enum parameter definition
struct ParameterEnum
{
    std::vector<EnumValue> values;

    ParameterEnum(const std::vector<EnumValue> &enum_values) : values(enum_values) {}

    // Get string name for uint8_t value
    std::string get_name(uint8_t value) const
    {
        for (const auto &enum_val : values)
        {
            if (enum_val.value == value)
            {
                return enum_val.name;
            }
        }
        return "UNKNOWN";
    }

    // Get uint8_t value for string name
    uint8_t get_value(const std::string &name) const
    {
        for (const auto &enum_val : values)
        {
            if (enum_val.name == name)
            {
                return enum_val.value;
            }
        }
        return 0; // Default to first value if not found
    }

    // Get all available names
    std::vector<std::string> get_names() const
    {
        std::vector<std::string> names;
        for (const auto &enum_val : values)
        {
            names.push_back(enum_val.name);
        }
        return names;
    }
};