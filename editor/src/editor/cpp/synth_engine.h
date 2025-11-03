/*
 * SynthEngine class for 4K Softsynth
 * Main synthesizer engine that manages multiple instruments
 */

#pragma once

#include <vector>
#include <memory>
#include <cstdint>
#include "instrument.h"
#include "parameters.h"

class SynthEngine
{
public:
    SynthEngine();

    bool initialize(void);

    Instrument *get_instrument(uint32_t instrument_id);
    const std::vector<std::unique_ptr<Instrument>> &get_all_instruments() const;
    uint32_t get_num_instruments() const;

    std::vector<float> render_note(void);
    std::vector<float> render_instrument_note(uint32_t instrument_num, uint32_t note_num);

    std::vector<int> get_instrument_instructions(uint32_t instrument_num);
    std::vector<uint8_t> get_instrument_instruction_parameters(uint32_t instrument_num, uint32_t instruction_index);
    std::vector<uint32_t> get_instrument_instruction_parameters_full(uint32_t instrument_num, uint32_t instruction_index);
    std::vector<ParameterRange> get_instrument_instruction_parameter_ranges(uint32_t instrument_num, uint32_t instruction_index);
    std::vector<uint8_t> get_instrument_instruction_parameter_types(uint32_t instrument_num, uint32_t instruction_index);
    std::vector<ParameterEnum> get_instrument_instruction_parameter_enums(uint32_t instrument_num, uint32_t instruction_index);
    std::vector<std::string> get_instrument_instruction_parameters_as_strings(uint32_t instrument_num, uint32_t instruction_index);

    bool update_instrument_parameter(uint32_t instrument_num, uint32_t instruction_index, uint32_t param_index, uint32_t value);
    bool update_instrument_parameter_with_string(uint32_t instrument_num, uint32_t instruction_index, uint32_t param_index, const std::string &value);

    bool is_initialized() const;

private:
    bool initialized_;
    std::vector<float> output_buffer_;
    std::vector<std::unique_ptr<Instrument>> instruments_;

    void create_instruments();
};