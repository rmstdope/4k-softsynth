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
        // The ARM64 softsynth doesn't require explicit initialization
        // but we can set up any needed state here
        initialized_ = true;
        DEBUG_LOG("Initialize completed successfully");
        return true;
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
        int num_samples = SAMPLES_PER_NOTE * 4;
        DEBUG_LOG("render_instrument_note called");
        std::vector<float> output(num_samples); // Mono output
        if (!initialized_)
        {
            DEBUG_LOG("Not initialized, returning silence");
            return output; // Return silence if not initialized
        }
        DEBUG_LOG("Setting up note");
        debug_start_instrument_note(instrument_num, note_num);
        // Hold for two notes and then release
        DEBUG_LOG("Render samples for instrument " << instrument_num);
        for (int i = 0; i < num_samples; i++)
        {
            if (i >= SAMPLES_PER_NOTE * 3)
                debug_next_instrument_sample(instrument_num, &output[i], 1);
            else
                debug_next_instrument_sample(instrument_num, &output[i], 0);
            // DEBUG_LOG("Sample " << i << ": " << std::fixed << std::setprecision(6) << output[i]);
            // if (i == 200)
            //     break;
        }
        // Trim trailing zero samples (allow tiny floating error)
        while (!output.empty() && std::fabs(output.back()) <= 1e-8f)
        {
            output.pop_back();
        }
        DEBUG_LOG("Trimmed output length to " << output.size());
        return output;
    }

    bool is_initialized() const
    {
        return initialized_;
    }

private:
    bool initialized_;
    std::vector<float> output_buffer_;
};

namespace py = pybind11;

PYBIND11_MODULE(synth_engine, m)
{
    m.doc() = "4K Softsynth Python bindings - ARM64 Assembly Interface";

    py::class_<SynthEngine>(m, "SynthEngine")
        .def(py::init<>())
        .def("initialize", &SynthEngine::initialize)
        .def("render_note", &SynthEngine::render_note)
        .def("is_initialized", &SynthEngine::is_initialized)
        .def("render_instrument_note", &SynthEngine::render_instrument_note, py::arg("instrument_num"), py::arg("note_num"));

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
    m.attr("OPERATION_ID") = OPERATION_ID;
    m.attr("FILTER_ID") = FILTER_ID;
    m.attr("PANNING_ID") = PANNING_ID;
    m.attr("OUTPUT_ID") = OUTPUT_ID;
    m.attr("INSTRUMENT_END") = INSTRUMENT_END;
}