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

// Include the actual softsynth headers
extern "C"
{
#include "../../softsynth/include/softsynth.h"
#include "../../softsynth/include/defines.h"
}

class SynthEngine
{
public:
    SynthEngine(int sample_rate = 44100, int buffer_size = 1024)
        : sample_rate_(sample_rate), buffer_size_(buffer_size), initialized_(false)
    {
        // Initialize output buffer
        output_buffer_.resize(buffer_size * 2); // Stereo output
    }

    bool initialize()
    {
        // The ARM64 softsynth doesn't require explicit initialization
        // but we can set up any needed state here
        initialized_ = true;
        return true;
    }

    std::vector<float> render_audio(int num_samples)
    {
        std::vector<float> output(num_samples * 2); // Stereo output

        if (!initialized_)
        {
            return output; // Return silence if not initialized
        }

        // Call the actual ARM64 softsynth render function
        // dope4ks_render expects (userdata, stream, len)
        // where len is in bytes, not samples
        int len_bytes = num_samples * 2 * sizeof(float); // Stereo float samples

        try
        {
            dope4ks_render(nullptr, reinterpret_cast<unsigned char *>(output.data()), len_bytes);
        }
        catch (...)
        {
            // If ARM64 assembly fails, generate a test tone
            for (int i = 0; i < num_samples; ++i)
            {
                float t = static_cast<float>(i) / sample_rate_;
                float sample = 0.1f * std::sin(2.0f * M_PI * 440.0f * t);
                output[i * 2] = sample;     // Left channel
                output[i * 2 + 1] = sample; // Right channel
            }
        }

        return output;
    }

    void set_transformed_parameter(int index, float value)
    {
        // Set values in the transformed_parameters array used by ARM64 code
        if (index >= 0 && index < 16)
        {
            transformed_parameters[index] = value;
        }
    }

    float get_transformed_parameter(int index) const
    {
        // Get values from the transformed_parameters array
        if (index >= 0 && index < 16)
        {
            return transformed_parameters[index];
        }
        return 0.0f;
    }

    void call_transform_values()
    {
        // Call the ARM64 transform_values function
        transform_values();
    }

    void call_envelope_function()
    {
        // Call the ARM64 envelope function
        envelope_function();
    }

    void call_storeval_function()
    {
        // Call the ARM64 storeval function
        storeval_function();
    }

    void call_process_stack()
    {
        // Call the ARM64 process_stack function
        process_stack();
    }

    void call_new_instrument_note()
    {
        // Call the ARM64 new_instrument_note function
        new_instrument_note();
    }

    // High-level interface functions
    void trigger_note(int instrument, int note, float velocity)
    {
        // Set up registers and call ARM64 assembly functions
        // This would need to set up the proper register state
        // and call new_instrument_note() with appropriate parameters
        call_new_instrument_note();
    }

    void set_envelope_parameters(float attack, float decay, float sustain, float release, float gain)
    {
        // Set ADSR parameters in transformed_parameters array
        // These indices match the ARM64 assembly expectations
        set_transformed_parameter(0, attack);  // ENVELOPE_PARAM_ATTACK
        set_transformed_parameter(1, decay);   // ENVELOPE_PARAM_DECAY
        set_transformed_parameter(2, sustain); // ENVELOPE_PARAM_SUSTAIN
        set_transformed_parameter(3, release); // ENVELOPE_PARAM_RELEASE
        set_transformed_parameter(4, gain);    // ENVELOPE_PARAM_GAIN
    }

    void set_oscillator_parameters(int type, float transpose, float detune, float color, float gain)
    {
        // Set oscillator parameters in transformed_parameters array
        set_transformed_parameter(5, static_cast<float>(type)); // OSCILLATOR_PARAM_TYPE
        set_transformed_parameter(6, transpose);                // OSCILLATOR_PARAM_TRANSPOSE
        set_transformed_parameter(7, detune);                   // OSCILLATOR_PARAM_DETUNE
        set_transformed_parameter(8, color);                    // OSCILLATOR_PARAM_COLOR
        set_transformed_parameter(9, gain);                     // OSCILLATOR_PARAM_GAIN
    }

    int get_sample_rate() const
    {
        return sample_rate_;
    }

    int get_buffer_size() const
    {
        return buffer_size_;
    }

    bool is_initialized() const
    {
        return initialized_;
    }

private:
    int sample_rate_;
    int buffer_size_;
    bool initialized_;
    std::vector<float> output_buffer_;
};

namespace py = pybind11;

PYBIND11_MODULE(synth_engine, m)
{
    m.doc() = "4K Softsynth Python bindings - ARM64 Assembly Interface";

    py::class_<SynthEngine>(m, "SynthEngine")
        .def(py::init<int, int>(), py::arg("sample_rate") = 44100, py::arg("buffer_size") = 1024)
        .def("initialize", &SynthEngine::initialize)
        .def("render_audio", &SynthEngine::render_audio)
        .def("trigger_note", &SynthEngine::trigger_note)
        .def("get_sample_rate", &SynthEngine::get_sample_rate)
        .def("get_buffer_size", &SynthEngine::get_buffer_size)
        .def("is_initialized", &SynthEngine::is_initialized)

        // Direct ARM64 assembly function calls
        .def("call_transform_values", &SynthEngine::call_transform_values)
        .def("call_envelope_function", &SynthEngine::call_envelope_function)
        .def("call_storeval_function", &SynthEngine::call_storeval_function)
        .def("call_process_stack", &SynthEngine::call_process_stack)
        .def("call_new_instrument_note", &SynthEngine::call_new_instrument_note)

        // Parameter access
        .def("set_transformed_parameter", &SynthEngine::set_transformed_parameter)
        .def("get_transformed_parameter", &SynthEngine::get_transformed_parameter)

        // High-level parameter setting
        .def("set_envelope_parameters", &SynthEngine::set_envelope_parameters,
             py::arg("attack"), py::arg("decay"), py::arg("sustain"), py::arg("release"), py::arg("gain"))
        .def("set_oscillator_parameters", &SynthEngine::set_oscillator_parameters,
             py::arg("type"), py::arg("transpose"), py::arg("detune"), py::arg("color"), py::arg("gain"));

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