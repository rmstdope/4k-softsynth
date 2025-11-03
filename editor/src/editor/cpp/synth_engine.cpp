/*
 * SynthEngine implementation for 4K Softsynth
 * Main synthesizer engine that manages multiple instruments
 */

#include "synth_engine.h"
#include "parameters.h"
#include <iostream>
#include <memory>

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

SynthEngine::SynthEngine()
    : initialized_(false)
{
    DEBUG_LOG("Constructor called");
    // Initialize output buffer
    // output_buffer_.resize(buffer_size * 2); // Stereo output
}

bool SynthEngine::initialize(void)
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

Instrument *SynthEngine::get_instrument(uint32_t instrument_id)
{
    if (instrument_id < instruments_.size())
    {
        return instruments_[instrument_id].get();
    }
    return nullptr;
}

const std::vector<std::unique_ptr<Instrument>> &SynthEngine::get_all_instruments() const
{
    return instruments_;
}

uint32_t SynthEngine::get_num_instruments() const
{
    return static_cast<uint32_t>(instruments_.size());
}

std::vector<float> SynthEngine::render_note(void)
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

std::vector<float> SynthEngine::render_instrument_note(uint32_t instrument_num, uint32_t note_num)
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

std::vector<int> SynthEngine::get_instrument_instructions(uint32_t instrument_num)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        return instrument->get_instructions();
    }
    return std::vector<int>();
}

std::vector<uint8_t> SynthEngine::get_instrument_instruction_parameters(uint32_t instrument_num, uint32_t instruction_index)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        return instrument->get_instruction_parameters(instruction_index);
    }
    return std::vector<uint8_t>();
}

std::vector<uint32_t> SynthEngine::get_instrument_instruction_parameters_full(uint32_t instrument_num, uint32_t instruction_index)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        return instrument->get_instruction_parameters_full(instruction_index);
    }
    return std::vector<uint32_t>();
}

std::vector<ParameterRange> SynthEngine::get_instrument_instruction_parameter_ranges(uint32_t instrument_num, uint32_t instruction_index)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        return instrument->get_instruction_parameter_ranges(instruction_index);
    }
    return std::vector<ParameterRange>();
}

std::vector<uint8_t> SynthEngine::get_instrument_instruction_parameter_types(uint32_t instrument_num, uint32_t instruction_index)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        return instrument->get_instruction_parameter_types(instruction_index);
    }
    return std::vector<uint8_t>();
}

std::vector<ParameterEnum> SynthEngine::get_instrument_instruction_parameter_enums(uint32_t instrument_num, uint32_t instruction_index)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        return instrument->get_instruction_parameter_enums(instruction_index);
    }
    return std::vector<ParameterEnum>();
}

std::vector<std::string> SynthEngine::get_instrument_instruction_parameters_as_strings(uint32_t instrument_num, uint32_t instruction_index)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        return instrument->get_instruction_parameters_as_strings(instruction_index);
    }
    return std::vector<std::string>();
}

bool SynthEngine::update_instrument_parameter(uint32_t instrument_num, uint32_t instruction_index, uint32_t param_index, uint32_t value)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        instrument->update_parameter(instruction_index, param_index, value);
        return true;
    }
    return false;
}

bool SynthEngine::update_instrument_parameter_with_string(uint32_t instrument_num, uint32_t instruction_index, uint32_t param_index, const std::string &value)
{
    Instrument *instrument = get_instrument(instrument_num);
    if (instrument)
    {
        instrument->update_parameter_with_string(instruction_index, param_index, value);
        return true;
    }
    return false;
}

bool SynthEngine::is_initialized() const
{
    return initialized_;
}

void SynthEngine::create_instruments()
{
    DEBUG_LOG("Creating " << MAX_NUM_INSTRUMENTS << " instruments");
    instruments_.clear();

    for (uint32_t i = 0; i < MAX_NUM_INSTRUMENTS; ++i)
    {
        instruments_.push_back(std::make_unique<Instrument>(i));
    }

    DEBUG_LOG("All instruments created successfully");
}