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

    const std::vector<std::vector<uint8_t>> &get_parameters() const { return parameters_; }

    std::vector<uint8_t> get_instruction_parameters(uint32_t instruction_index) const
    {
        if (instruction_index < parameters_.size())
        {
            return parameters_[instruction_index];
        }
        return std::vector<uint8_t>();
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

    std::string get_instruction_name(uint32_t instruction_index) const
    {
        if (instruction_index >= instructions_.size())
        {
            return "UNKNOWN";
        }

        int instruction_id = instructions_[instruction_index];
        return get_instruction_name_by_id(instruction_id);
    }

    void update_parameter(uint32_t instruction_index, uint32_t param_index, uint8_t value)
    {
        if (instruction_index < parameters_.size() && param_index < parameters_[instruction_index].size())
        {
            parameters_[instruction_index][param_index] = value;
            DEBUG_LOG("Updated Instrument " << id_ << " instruction " << instruction_index
                                            << " param " << param_index << " to " << static_cast<int>(value));
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
    std::vector<std::vector<uint8_t>> parameters_;

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

        // Load parameters for our instrument
        for (size_t i = 0; i < instructions_.size(); ++i)
        {
            uint32_t num_params = get_instruction_param_count(instructions_[i]);
            std::vector<uint8_t> instruction_params;

            for (uint32_t j = 0; j < num_params; ++j)
            {
                instruction_params.push_back(param_ptr[j]);
            }

            parameters_.push_back(instruction_params);
            param_ptr += num_params;
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
            return 3;
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
            return {"Amount", "Destination1", "Destination2"};
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

    bool update_instrument_parameter(uint32_t instrument_num, uint32_t instruction_index, uint32_t param_index, uint8_t value)
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

    py::class_<Instrument>(m, "Instrument")
        .def("get_id", &Instrument::get_id)
        .def("get_instructions", &Instrument::get_instructions)
        .def("get_instruction_parameters", &Instrument::get_instruction_parameters, py::arg("instruction_index"))
        .def("get_instruction_parameter_names", &Instrument::get_instruction_parameter_names, py::arg("instruction_index"))
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
}