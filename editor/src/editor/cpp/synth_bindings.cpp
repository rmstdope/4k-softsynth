/*
 * Python C++ Extension for 4K Softsynth
 * Provides Python bindings using pybind11 to the ARM64 assembly synthesizer
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>
#include <cmath>
#include <cstring>
#include <iostream>
#include <iomanip>
#include <memory>
#include <string>
#include "instrument.h"
#include "synth_engine.h"
#include "parameters.h"

// Debug logging macro
#ifdef DEBUG
#define DEBUG_LOG(msg) std::cout << "[DEBUG] SynthEngine: " << msg << std::endl
#else
#define DEBUG_LOG(msg) \
    do                 \
    {                  \
    } while (0)
#endif

// Include the actual softsynth headers
extern "C"
{
#include "../../softsynth/include/softsynth.h"
#include "../../softsynth/include/defines.h"
}

#define INSTRUMENT_SIZE (3 + MAX_COMMANDS * MAX_COMMAND_PARAMS)
#define SYNTH_SIZE INSTRUMENT_SIZE *MAX_NUM_INSTRUMENTS

namespace py = pybind11;

PYBIND11_MODULE(synth_engine, m)
{
    m.doc() = "4K Softsynth Python bindings - ARM64 Assembly Interface";

    // Expose ParameterRange struct
    py::class_<ParameterRange>(m, "ParameterRange")
        .def(py::init<int, int, int>(), py::arg("min_value"), py::arg("max_value"), py::arg("step") = 1)
        .def_readwrite("min_value", &ParameterRange::min_value)
        .def_readwrite("max_value", &ParameterRange::max_value)
        .def_readwrite("step", &ParameterRange::step)
        .def("__repr__", [](const ParameterRange &pr)
             { return "ParameterRange(min=" + std::to_string(pr.min_value) +
                      ", max=" + std::to_string(pr.max_value) +
                      ", step=" + std::to_string(pr.step) + ")"; });

    // Expose EnumValue struct
    py::class_<EnumValue>(m, "EnumValue")
        .def(py::init<uint8_t, const std::string &>(), py::arg("value"), py::arg("name"))
        .def_readwrite("value", &EnumValue::value)
        .def_readwrite("name", &EnumValue::name)
        .def("__repr__", [](const EnumValue &ev)
             { return "EnumValue(value=" + std::to_string(ev.value) + ", name=\"" + ev.name + "\")"; });

    // Expose ParameterEnum struct
    py::class_<ParameterEnum>(m, "ParameterEnum")
        .def(py::init<const std::vector<EnumValue> &>(), py::arg("values"))
        .def("get_name", &ParameterEnum::get_name, py::arg("value"))
        .def("get_value", &ParameterEnum::get_value, py::arg("name"))
        .def("get_names", &ParameterEnum::get_names)
        .def_readwrite("values", &ParameterEnum::values)
        .def("__repr__", [](const ParameterEnum &pe)
             { return "ParameterEnum(values=" + std::to_string(pe.values.size()) + " items)"; });

    py::class_<Instrument>(m, "Instrument")
        .def("get_id", &Instrument::get_id)
        .def("get_instructions", &Instrument::get_instructions)
        .def("get_instruction_parameters", &Instrument::get_instruction_parameters, py::arg("instruction_index"))
        .def("get_instruction_parameters_full", &Instrument::get_instruction_parameters_full, py::arg("instruction_index"))
        .def("get_instruction_parameter_names", &Instrument::get_instruction_parameter_names, py::arg("instruction_index"))
        .def("get_instruction_parameter_ranges", &Instrument::get_instruction_parameter_ranges, py::arg("instruction_index"))
        .def("get_instruction_parameter_types", &Instrument::get_instruction_parameter_types, py::arg("instruction_index"))
        .def("get_instruction_parameter_enums", &Instrument::get_instruction_parameter_enums, py::arg("instruction_index"))
        .def("get_instruction_parameters_as_strings", &Instrument::get_instruction_parameters_as_strings, py::arg("instruction_index"))
        .def("get_instruction_name", &Instrument::get_instruction_name, py::arg("instruction_index"))
        .def("update_parameter", &Instrument::update_parameter, py::arg("instruction_index"), py::arg("param_index"), py::arg("value"))
        .def("update_parameter_with_string", &Instrument::update_parameter_with_string, py::arg("instruction_index"), py::arg("param_index"), py::arg("value"))
        .def("render_note", &Instrument::render_note, py::arg("note_num"));

    py::class_<SynthEngine>(m, "SynthEngine")
        .def(py::init<>())
        .def("initialize", &SynthEngine::initialize)
        .def("render_note", &SynthEngine::render_note)
        .def("is_initialized", &SynthEngine::is_initialized)
        .def("render_instrument_note", &SynthEngine::render_instrument_note, py::arg("instrument_num"), py::arg("note_num"))
        .def("get_instrument", &SynthEngine::get_instrument, py::arg("instrument_id"), py::return_value_policy::reference_internal)
        .def("get_num_instruments", &SynthEngine::get_num_instruments)
        .def("get_instrument_instructions", &SynthEngine::get_instrument_instructions, py::arg("instrument_num"))
        .def("get_instrument_instruction_parameters", &SynthEngine::get_instrument_instruction_parameters, py::arg("instrument_num"), py::arg("instruction_index"))
        .def("get_instrument_instruction_parameters_full", &SynthEngine::get_instrument_instruction_parameters_full, py::arg("instrument_num"), py::arg("instruction_index"))
        .def("get_instrument_instruction_parameter_ranges", &SynthEngine::get_instrument_instruction_parameter_ranges, py::arg("instrument_num"), py::arg("instruction_index"))
        .def("get_instrument_instruction_parameter_types", &SynthEngine::get_instrument_instruction_parameter_types, py::arg("instrument_num"), py::arg("instruction_index"))
        .def("get_instrument_instruction_parameter_enums", &SynthEngine::get_instrument_instruction_parameter_enums, py::arg("instrument_num"), py::arg("instruction_index"))
        .def("get_instrument_instruction_parameters_as_strings", &SynthEngine::get_instrument_instruction_parameters_as_strings, py::arg("instrument_num"), py::arg("instruction_index"))
        .def("update_instrument_parameter", &SynthEngine::update_instrument_parameter, py::arg("instrument_num"), py::arg("instruction_index"), py::arg("param_index"), py::arg("value"))
        .def("update_instrument_parameter_with_string", &SynthEngine::update_instrument_parameter_with_string, py::arg("instrument_num"), py::arg("instruction_index"), py::arg("param_index"), py::arg("value"));

    // Expose constants from defines.h
    m.attr("SAMPLE_RATE") = SAMPLE_RATE;
    m.attr("BEATS_PER_MINUTE") = BEATS_PER_MINUTE;
    m.attr("NOTES_PER_BEAT") = NOTES_PER_BEAT;
    m.attr("SAMPLES_PER_NOTE") = SAMPLES_PER_NOTE;
    m.attr("MAX_NUM_INSTRUMENTS") = MAX_NUM_INSTRUMENTS;
    m.attr("MAX_COMMANDS") = MAX_COMMANDS;
    m.attr("MAX_COMMAND_PARAMS") = MAX_COMMAND_PARAMS;
    m.attr("PATTERNS_PER_INSTRUMENT") = PATTERNS_PER_INSTRUMENT;
    m.attr("NOTES_PER_PATTERN") = NOTES_PER_PATTERN;
    m.attr("HLD") = HLD;

    // Instruction IDs
    m.attr("ENVELOPE_ID") = ENVELOPE_ID;
    m.attr("OSCILLATOR_ID") = OSCILLATOR_ID;
    m.attr("STOREVAL_ID") = STOREVAL_ID;
    m.attr("OPERATION_ID") = OPERATION_ID;
    m.attr("FILTER_ID") = FILTER_ID;
    m.attr("PANNING_ID") = PANNING_ID;
    m.attr("OUTPUT_ID") = OUTPUT_ID;
    m.attr("INSTRUMENT_END") = INSTRUMENT_END;

    // Parameter Types
    m.attr("PARAM_TYPE_UINT8") = static_cast<uint8_t>(ParameterType::UINT8);
    m.attr("PARAM_TYPE_UINT16") = static_cast<uint8_t>(ParameterType::UINT16);
    m.attr("PARAM_TYPE_ENUM") = static_cast<uint8_t>(ParameterType::ENUM);
}