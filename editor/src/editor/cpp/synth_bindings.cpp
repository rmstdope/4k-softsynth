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

// Parameter data types
enum class ParameterType : uint8_t
{
    UINT8 = 0,
    UINT16 = 1
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

class Instrument
{
public:
    Instrument(uint32_t instrument_id) : id_(instrument_id)
    {
        DEBUG_LOG("Creating Instrument " << instrument_id);
        load_instructions_and_parameters();
    }

    uint32_t get_id() const { return id_; }

    const std::vector<int> &get_instructions() const { return instructions_; }

    const std::vector<std::vector<uint8_t *>> &get_parameters() const { return parameters_; }

    std::vector<uint8_t> get_instruction_parameters(uint32_t instruction_index) const
    {
        if (instruction_index < parameters_.size())
        {
            std::vector<uint8_t> values;
            int instruction_id = instructions_[instruction_index];
            std::vector<uint8_t> param_types = get_parameter_types_for_instruction(instruction_id);

            size_t ptr_idx = 0;

            for (size_t i = 0; i < param_types.size() && ptr_idx < parameters_[instruction_index].size(); ++i)
            {
                if (param_types[i] == static_cast<uint8_t>(ParameterType::UINT8))
                {
                    // Single uint8_t parameter
                    values.push_back(*parameters_[instruction_index][ptr_idx]);
                    ptr_idx++;
                }
                else if (param_types[i] == static_cast<uint8_t>(ParameterType::UINT16))
                {
                    // uint16_t parameter stored as two consecutive uint8_t values (little-endian)
                    if (ptr_idx + 1 < parameters_[instruction_index].size())
                    {
                        uint16_t value = *parameters_[instruction_index][ptr_idx] |
                                         (*parameters_[instruction_index][ptr_idx + 1] << 8);
                        // For Python interface, we'll return the low byte for compatibility
                        // The actual uint16 value will be handled by a separate method
                        values.push_back(value & 0xFF);
                        ptr_idx += 2;
                    }
                    else
                    {
                        values.push_back(0);
                        ptr_idx++;
                    }
                }
            }
            return values;
        }
        return std::vector<uint8_t>();
    }

    std::vector<uint32_t> get_instruction_parameters_full(uint32_t instruction_index) const
    {
        if (instruction_index < parameters_.size())
        {
            std::vector<uint32_t> values;
            int instruction_id = instructions_[instruction_index];
            std::vector<uint8_t> param_types = get_parameter_types_for_instruction(instruction_id);

            size_t ptr_idx = 0;

            for (size_t i = 0; i < param_types.size() && ptr_idx < parameters_[instruction_index].size(); ++i)
            {
                if (param_types[i] == static_cast<uint8_t>(ParameterType::UINT8))
                {
                    // Single uint8_t parameter
                    values.push_back(static_cast<uint32_t>(*parameters_[instruction_index][ptr_idx]));
                    ptr_idx++;
                }
                else if (param_types[i] == static_cast<uint8_t>(ParameterType::UINT16))
                {
                    // uint16_t parameter stored as two consecutive uint8_t values (little-endian)
                    if (ptr_idx < parameters_[instruction_index].size())
                    {
                        uint8_t *param_ptr = parameters_[instruction_index][ptr_idx];
                        uint16_t value = param_ptr[0] | (param_ptr[1] << 8);
                        values.push_back(static_cast<uint32_t>(value));
                        ptr_idx++;
                    }
                    else
                    {
                        values.push_back(0);
                        ptr_idx++;
                    }
                }
            }
            return values;
        }
        return std::vector<uint32_t>();
    }

    std::vector<std::string> get_instruction_parameter_names(uint32_t instruction_index) const
    {
        if (instruction_index >= instructions_.size())
        {
            return std::vector<std::string>();
        }

        int instruction_id = instructions_[instruction_index];
        return get_parameter_names_for_instruction(instruction_id);
    }

    std::vector<ParameterRange> get_instruction_parameter_ranges(uint32_t instruction_index) const
    {
        if (instruction_index >= instructions_.size())
        {
            return std::vector<ParameterRange>();
        }

        int instruction_id = instructions_[instruction_index];
        return get_parameter_ranges_for_instruction(instruction_id);
    }

    std::vector<uint8_t> get_instruction_parameter_types(uint32_t instruction_index) const
    {
        if (instruction_index >= instructions_.size())
        {
            return std::vector<uint8_t>();
        }

        int instruction_id = instructions_[instruction_index];
        return get_parameter_types_for_instruction(instruction_id);
    }

    std::string get_instruction_name(uint32_t instruction_index) const
    {
        if (instruction_index >= instructions_.size())
        {
            return "UNKNOWN";
        }

        int instruction_id = instructions_[instruction_index];
        return get_instruction_name_by_id(instruction_id);
    }

    void update_parameter(uint32_t instruction_index, uint32_t param_index, uint32_t value)
    {
        if (instruction_index < parameters_.size())
        {
            int instruction_id = instructions_[instruction_index];
            std::vector<uint8_t> param_types = get_parameter_types_for_instruction(instruction_id);

            if (param_index < param_types.size())
            {
                // Calculate the memory pointer index based on parameter types
                size_t ptr_idx = 0;
                for (size_t i = 0; i < param_index; ++i)
                {
                    if (param_types[i] == static_cast<uint8_t>(ParameterType::UINT16))
                    {
                        ptr_idx += 2; // uint16 takes 2 bytes
                    }
                    else
                    {
                        ptr_idx += 1; // uint8 takes 1 byte
                    }
                }

                if (param_types[param_index] == static_cast<uint8_t>(ParameterType::UINT8))
                {
                    // Update uint8_t parameter
                    if (ptr_idx < parameters_[instruction_index].size())
                    {
                        *(parameters_[instruction_index][ptr_idx]) = static_cast<uint8_t>(value & 0xFF);
                        DEBUG_LOG("Updated Instrument " << id_ << " instruction " << instruction_index
                                                        << " param " << param_index << " (uint8) to " << static_cast<int>(value & 0xFF));
                    }
                }
                else if (param_types[param_index] == static_cast<uint8_t>(ParameterType::UINT16))
                {
                    // Update uint16_t parameter (stored as two consecutive uint8_t values, little-endian)
                    if (ptr_idx < parameters_[instruction_index].size())
                    {
                        uint16_t value16 = static_cast<uint16_t>(value & 0xFFFF);
                        uint8_t *param_ptr = parameters_[instruction_index][ptr_idx];
                        param_ptr[0] = static_cast<uint8_t>(value16 & 0xFF);        // Low byte
                        param_ptr[1] = static_cast<uint8_t>((value16 >> 8) & 0xFF); // High byte
                        DEBUG_LOG("Updated Instrument " << id_ << " instruction " << instruction_index
                                                        << " param " << param_index << " (uint16) to " << static_cast<int>(value16));
                    }
                }
            }
        }
    }

    std::vector<float> render_note(uint32_t note_num)
    {
        int num_samples = SAMPLES_PER_NOTE * 4;
        DEBUG_LOG("Instrument " << id_ << " rendering note " << note_num);
        std::vector<float> output(num_samples);

        debug_start_instrument_note(id_, note_num);

        // Render samples with hold and release phases
        for (int i = 0; i < num_samples; i++)
        {
            uint8_t release = (i >= SAMPLES_PER_NOTE * 3) ? 1 : 0;
            debug_next_instrument_sample(id_, &output[i], release);
        }

        // Trim trailing zero samples
        while (!output.empty() && std::fabs(output.back()) <= 1e-8f)
        {
            output.pop_back();
        }

        DEBUG_LOG("Instrument " << id_ << " rendered " << output.size() << " samples");
        return output;
    }

private:
    uint32_t id_;
    std::vector<int> instructions_;
    std::vector<std::vector<uint8_t *>> parameters_; // Store pointers to actual parameter locations

    void load_instructions_and_parameters()
    {
        DEBUG_LOG("Loading instructions and parameters for instrument " << id_);

        // Load instructions
        uint8_t *instr_ptr = instrument_instructions;
        uint32_t current_instrument = 0;

        // Navigate to the correct instrument
        while (current_instrument < id_)
        {
            while (instr_ptr[0] != INSTRUMENT_END)
            {
                instr_ptr++;
            }
            instr_ptr++; // Move past END
            current_instrument++;
        }

        // Read instructions for this instrument
        while (*instr_ptr != INSTRUMENT_END)
        {
            instructions_.push_back(static_cast<int>(*instr_ptr));
            instr_ptr++;
        }

        // Load parameters
        load_parameters_for_instructions();

        DEBUG_LOG("Instrument " << id_ << " loaded " << instructions_.size() << " instructions");
    }

    void load_parameters_for_instructions()
    {
        uint8_t *param_ptr = instrument_parameters;
        uint32_t current_instrument = 0;

        // Navigate to the correct instrument's parameters
        while (current_instrument < id_)
        {
            uint8_t *temp_instr_ptr = instrument_instructions;
            uint32_t temp_instrument = 0;

            // Skip to current instrument in instruction stream
            while (temp_instrument < current_instrument)
            {
                while (temp_instr_ptr[0] != INSTRUMENT_END)
                {
                    temp_instr_ptr++;
                }
                temp_instr_ptr++;
                temp_instrument++;
            }

            // Count parameters for this instrument
            while (temp_instr_ptr[0] != INSTRUMENT_END)
            {
                uint32_t num_params = get_instruction_param_count(temp_instr_ptr[0]);
                param_ptr += num_params;
                temp_instr_ptr++;
            }
            current_instrument++;
        }

        // Load parameter pointers for our instrument
        for (size_t i = 0; i < instructions_.size(); ++i)
        {
            int instruction_id = instructions_[i];
            std::vector<uint8_t> param_types = get_parameter_types_for_instruction(instruction_id);
            std::vector<uint8_t *> instruction_param_ptrs;

            uint32_t memory_offset = 0;
            for (size_t j = 0; j < param_types.size(); ++j)
            {
                instruction_param_ptrs.push_back(&param_ptr[memory_offset]);

                if (param_types[j] == static_cast<uint8_t>(ParameterType::UINT16))
                {
                    memory_offset += 2; // uint16 takes 2 bytes
                }
                else
                {
                    memory_offset += 1; // uint8 takes 1 byte
                }
            }

            parameters_.push_back(instruction_param_ptrs);

            // Move param_ptr by the total memory used by this instruction
            // This should match the original memory layout from the ARM64 assembly
            uint32_t memory_size = get_instruction_memory_size(instruction_id);
            param_ptr += memory_size;
        }
    }

    uint32_t get_instruction_param_count(int instruction_id) const
    {
        switch (instruction_id)
        {
        case ENVELOPE_ID:
            return 5;
        case OSCILLATOR_ID:
            return 8;
        case STOREVAL_ID:
            return 2; // Changed from 3 to 2: Amount + merged Destination
        case OPERATION_ID:
            return 1;
        case OUTPUT_ID:
            return 1;
        case FILTER_ID:
        case PANNING_ID:
            return 1; // Assuming 1 parameter each
        default:
            return 0;
        }
    }

    uint32_t get_instruction_memory_size(int instruction_id) const
    {
        switch (instruction_id)
        {
        case ENVELOPE_ID:
            return 5; // 5 uint8 parameters
        case OSCILLATOR_ID:
            return 8; // 8 uint8 parameters
        case STOREVAL_ID:
            return 3; // Amount (1 byte) + Destination (2 bytes) = 3 bytes total
        case OPERATION_ID:
            return 1; // 1 uint8 parameter
        case OUTPUT_ID:
            return 1; // 1 uint8 parameter
        case FILTER_ID:
        case PANNING_ID:
            return 1; // 1 uint8 parameter each
        default:
            return 0;
        }
    }

    std::string get_instruction_name_by_id(int instruction_id) const
    {
        switch (instruction_id)
        {
        case ENVELOPE_ID:
            return "ENVELOPE";
        case OSCILLATOR_ID:
            return "OSCILLATOR";
        case STOREVAL_ID:
            return "STOREVAL";
        case OPERATION_ID:
            return "OPERATION";
        case OUTPUT_ID:
            return "OUTPUT";
        case FILTER_ID:
            return "FILTER";
        case PANNING_ID:
            return "PANNING";
        case ACCUMULATE_ID:
            return "ACCUMULATE";
        default:
            return "UNKNOWN_" + std::to_string(instruction_id);
        }
    }

    std::vector<std::string> get_parameter_names_for_instruction(int instruction_id) const
    {
        switch (instruction_id)
        {
        case ENVELOPE_ID:
            return {"Attack", "Decay", "Sustain", "Release", "Gain"};
        case OSCILLATOR_ID:
            return {"Transpose", "Detune", "Phase", "Gates", "Color", "Shape", "Gain", "Type"};
        case STOREVAL_ID:
            return {"Amount", "Destination"};
        case OPERATION_ID:
            return {"Operand"};
        case OUTPUT_ID:
            return {"Gain"};
        case FILTER_ID:
            return {"Cutoff"};
        case PANNING_ID:
            return {"Position"};
        case ACCUMULATE_ID:
            return {}; // No parameters
        default:
            return {};
        }
    }

    std::vector<ParameterRange> get_parameter_ranges_for_instruction(int instruction_id) const
    {
        switch (instruction_id)
        {
        case ENVELOPE_ID:
            // Attack, Decay, Sustain, Release, Gain (all default step=1)
            return {ParameterRange(0, 255), ParameterRange(0, 255), ParameterRange(0, 255),
                    ParameterRange(0, 255), ParameterRange(0, 128)};
        case OSCILLATOR_ID:
            // Transpose, Detune, Phase, Gates, Color, Shape, Gain, Type (some with custom steps)
            return {ParameterRange(0, 127), ParameterRange(0, 255), ParameterRange(0, 255),
                    ParameterRange(0, 15), ParameterRange(0, 255), ParameterRange(0, 7),
                    ParameterRange(0, 128), ParameterRange(0, 7)};
        case STOREVAL_ID:
            // Amount (step=1), Destination (uint16, larger step for coarse control)
            return {ParameterRange(0, 255), ParameterRange(0, 65535, 4)};
        case OPERATION_ID:
            // Operand (step=1)
            return {ParameterRange(0, 15)};
        case OUTPUT_ID:
            // Gain (step=1)
            return {ParameterRange(0, 128)};
        case FILTER_ID:
            // Cutoff (step=1)
            return {ParameterRange(0, 255)};
        case PANNING_ID:
            // Position (-64 to +63, but we'll map 0-127, step=1)
            return {ParameterRange(0, 127)};
        case ACCUMULATE_ID:
            return {}; // No parameters
        default:
            return {};
        }
    }

    std::vector<uint8_t> get_parameter_types_for_instruction(int instruction_id) const
    {
        switch (instruction_id)
        {
        case ENVELOPE_ID:
            // Attack, Decay, Sustain, Release, Gain - all uint8_t for now
            return {static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8)};
        case OSCILLATOR_ID:
            // Transpose, Detune, Phase, Gates, Color, Shape, Gain, Type - all uint8_t for now
            return {static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT8)};
        case STOREVAL_ID:
            // Amount (uint8), Destination (uint16)
            return {static_cast<uint8_t>(ParameterType::UINT8),
                    static_cast<uint8_t>(ParameterType::UINT16)};
        case OPERATION_ID:
            // Operand - uint8_t for now
            return {static_cast<uint8_t>(ParameterType::UINT8)};
        case OUTPUT_ID:
            // Gain - uint8_t for now
            return {static_cast<uint8_t>(ParameterType::UINT8)};
        case FILTER_ID:
            // Cutoff - uint8_t for now
            return {static_cast<uint8_t>(ParameterType::UINT8)};
        case PANNING_ID:
            // Position - uint8_t for now
            return {static_cast<uint8_t>(ParameterType::UINT8)};
        case ACCUMULATE_ID:
            return {}; // No parameters
        default:
            return {};
        }
    }
};

class SynthEngine
{
public:
    SynthEngine()
        : initialized_(false)
    {
        DEBUG_LOG("Constructor called");
        // Initialize output buffer
        // output_buffer_.resize(buffer_size * 2); // Stereo output
    }

    bool initialize(void)
    {
        DEBUG_LOG("Initialize called");

        // Create all instruments
        create_instruments();

        // The ARM64 softsynth doesn't require explicit initialization
        // but we can set up any needed state here
        initialized_ = true;
        DEBUG_LOG("Initialize completed successfully");
        return true;
    }

    Instrument *get_instrument(uint32_t instrument_id)
    {
        if (instrument_id < instruments_.size())
        {
            return instruments_[instrument_id].get();
        }
        return nullptr;
    }

    const std::vector<std::unique_ptr<Instrument>> &get_all_instruments() const
    {
        return instruments_;
    }

    uint32_t get_num_instruments() const
    {
        return static_cast<uint32_t>(instruments_.size());
    }

    std::vector<float> render_note(void)
    {
        DEBUG_LOG("render_note called");
        std::vector<float> output(SAMPLES_PER_NOTE); // Mono output

        if (!initialized_)
        {
            DEBUG_LOG("Not initialized, returning silence");
            return output; // Return silence if not initialized
        }

        // Call the actual ARM64 softsynth render function
        // dope4ks_render expects (userdata, stream, len)
        // where len is in bytes, not samples
        int len_bytes = SAMPLES_PER_NOTE * 2 * sizeof(float); // Stereo float samples
        DEBUG_LOG("Calling dope4ks_render with " << len_bytes << " bytes");

        dope4ks_render(nullptr, reinterpret_cast<unsigned char *>(output.data()), len_bytes);
        DEBUG_LOG("dope4ks_render completed");

        return output;
    }

    std::vector<float> render_instrument_note(uint32_t instrument_num, uint32_t note_num)
    {
        DEBUG_LOG("render_instrument_note called for instrument " << instrument_num);

        if (!initialized_)
        {
            DEBUG_LOG("Not initialized, returning silence");
            return std::vector<float>(SAMPLES_PER_NOTE * 4); // Return silence
        }

        Instrument *instrument = get_instrument(instrument_num);
        if (!instrument)
        {
            DEBUG_LOG("Invalid instrument " << instrument_num << ", returning silence");
            return std::vector<float>(SAMPLES_PER_NOTE * 4); // Return silence
        }

        return instrument->render_note(note_num);
    }

    std::vector<int> get_instrument_instructions(uint32_t instrument_num)
    {
        Instrument *instrument = get_instrument(instrument_num);
        if (instrument)
        {
            return instrument->get_instructions();
        }
        return std::vector<int>();
    }

    std::vector<uint8_t> get_instrument_instruction_parameters(uint32_t instrument_num, uint32_t instruction_index)
    {
        Instrument *instrument = get_instrument(instrument_num);
        if (instrument)
        {
            return instrument->get_instruction_parameters(instruction_index);
        }
        return std::vector<uint8_t>();
    }

    std::vector<uint32_t> get_instrument_instruction_parameters_full(uint32_t instrument_num, uint32_t instruction_index)
    {
        Instrument *instrument = get_instrument(instrument_num);
        if (instrument)
        {
            return instrument->get_instruction_parameters_full(instruction_index);
        }
        return std::vector<uint32_t>();
    }

    std::vector<ParameterRange> get_instrument_instruction_parameter_ranges(uint32_t instrument_num, uint32_t instruction_index)
    {
        Instrument *instrument = get_instrument(instrument_num);
        if (instrument)
        {
            return instrument->get_instruction_parameter_ranges(instruction_index);
        }
        return std::vector<ParameterRange>();
    }

    std::vector<uint8_t> get_instrument_instruction_parameter_types(uint32_t instrument_num, uint32_t instruction_index)
    {
        Instrument *instrument = get_instrument(instrument_num);
        if (instrument)
        {
            return instrument->get_instruction_parameter_types(instruction_index);
        }
        return std::vector<uint8_t>();
    }

    bool update_instrument_parameter(uint32_t instrument_num, uint32_t instruction_index, uint32_t param_index, uint32_t value)
    {
        Instrument *instrument = get_instrument(instrument_num);
        if (instrument)
        {
            instrument->update_parameter(instruction_index, param_index, value);
            return true;
        }
        return false;
    }

    bool is_initialized() const
    {
        return initialized_;
    }

private:
    bool initialized_;
    std::vector<float> output_buffer_;
    std::vector<std::unique_ptr<Instrument>> instruments_;

    void create_instruments()
    {
        DEBUG_LOG("Creating " << MAX_NUM_INSTRUMENTS << " instruments");
        instruments_.clear();

        for (uint32_t i = 0; i < MAX_NUM_INSTRUMENTS; ++i)
        {
            instruments_.push_back(std::make_unique<Instrument>(i));
        }

        DEBUG_LOG("All instruments created successfully");
    }
};

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

    py::class_<Instrument>(m, "Instrument")
        .def("get_id", &Instrument::get_id)
        .def("get_instructions", &Instrument::get_instructions)
        .def("get_instruction_parameters", &Instrument::get_instruction_parameters, py::arg("instruction_index"))
        .def("get_instruction_parameters_full", &Instrument::get_instruction_parameters_full, py::arg("instruction_index"))
        .def("get_instruction_parameter_names", &Instrument::get_instruction_parameter_names, py::arg("instruction_index"))
        .def("get_instruction_parameter_ranges", &Instrument::get_instruction_parameter_ranges, py::arg("instruction_index"))
        .def("get_instruction_parameter_types", &Instrument::get_instruction_parameter_types, py::arg("instruction_index"))
        .def("get_instruction_name", &Instrument::get_instruction_name, py::arg("instruction_index"))
        .def("update_parameter", &Instrument::update_parameter, py::arg("instruction_index"), py::arg("param_index"), py::arg("value"))
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
        .def("update_instrument_parameter", &SynthEngine::update_instrument_parameter, py::arg("instrument_num"), py::arg("instruction_index"), py::arg("param_index"), py::arg("value"));

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
}