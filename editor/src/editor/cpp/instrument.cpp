/*
 * Instrument class implementation for 4K Softsynth
 * Represents a single synthesizer instrument with parameters and rendering capabilities
 */

#include "instrument.h"
#include "parameters.h"
#include <iostream>
#include <iomanip>
#include <cmath>

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

Instrument::Instrument(uint32_t instrument_id) : id_(instrument_id)
{
    DEBUG_LOG("Creating Instrument " << instrument_id);
    load_instructions_and_parameters();
}

std::vector<uint8_t> Instrument::get_instruction_parameters(uint32_t instruction_index) const
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
                if (ptr_idx < parameters_[instruction_index].size())
                {
                    uint8_t *param_ptr = parameters_[instruction_index][ptr_idx];
                    uint16_t value = param_ptr[0] | (param_ptr[1] << 8);
                    // For Python interface, we'll return the low byte for compatibility
                    // The actual uint16 value will be handled by a separate method
                    values.push_back(value & 0xFF);
                    ptr_idx++;
                }
                else
                {
                    values.push_back(0);
                    ptr_idx++;
                }
            }
            else if (param_types[i] == static_cast<uint8_t>(ParameterType::ENUM))
            {
                // ENUM parameter stored as single uint8_t value
                values.push_back(*parameters_[instruction_index][ptr_idx]);
                ptr_idx++;
            }
        }
        return values;
    }
    return std::vector<uint8_t>();
}

std::vector<uint32_t> Instrument::get_instruction_parameters_full(uint32_t instruction_index) const
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
            else if (param_types[i] == static_cast<uint8_t>(ParameterType::ENUM))
            {
                // Enum parameter stored as uint8_t value
                values.push_back(static_cast<uint32_t>(*parameters_[instruction_index][ptr_idx]));
                ptr_idx++;
            }
        }
        return values;
    }
    return std::vector<uint32_t>();
}

std::vector<std::string> Instrument::get_instruction_parameters_as_strings(uint32_t instruction_index) const
{
    if (instruction_index < parameters_.size())
    {
        std::vector<std::string> values;
        int instruction_id = instructions_[instruction_index];
        std::vector<uint8_t> param_types = get_parameter_types_for_instruction(instruction_id);
        std::vector<ParameterEnum> param_enums = get_parameter_enums_for_instruction(instruction_id);

        size_t ptr_idx = 0;

        for (size_t i = 0; i < param_types.size() && ptr_idx < parameters_[instruction_index].size(); ++i)
        {
            if (param_types[i] == static_cast<uint8_t>(ParameterType::UINT8))
            {
                // Single uint8_t parameter - convert to string
                values.push_back(std::to_string(*parameters_[instruction_index][ptr_idx]));
                ptr_idx++;
            }
            else if (param_types[i] == static_cast<uint8_t>(ParameterType::UINT16))
            {
                // uint16_t parameter - convert to string
                if (ptr_idx < parameters_[instruction_index].size())
                {
                    uint8_t *param_ptr = parameters_[instruction_index][ptr_idx];
                    uint16_t value = param_ptr[0] | (param_ptr[1] << 8);
                    values.push_back(std::to_string(value));
                    ptr_idx++;
                }
                else
                {
                    values.push_back("0");
                    ptr_idx++;
                }
            }
            else if (param_types[i] == static_cast<uint8_t>(ParameterType::ENUM))
            {
                // Enum parameter - convert uint8_t to string name
                uint8_t enum_value = *parameters_[instruction_index][ptr_idx];
                if (i < param_enums.size() && !param_enums[i].values.empty())
                {
                    values.push_back(param_enums[i].get_name(enum_value));
                }
                else
                {
                    values.push_back(std::to_string(enum_value));
                }
                ptr_idx++;
            }
        }
        return values;
    }
    return std::vector<std::string>();
}

std::vector<std::string> Instrument::get_instruction_parameter_names(uint32_t instruction_index) const
{
    if (instruction_index >= instructions_.size())
    {
        return std::vector<std::string>();
    }

    int instruction_id = instructions_[instruction_index];
    return get_parameter_names_for_instruction(instruction_id);
}

std::vector<ParameterRange> Instrument::get_instruction_parameter_ranges(uint32_t instruction_index) const
{
    if (instruction_index >= instructions_.size())
    {
        return std::vector<ParameterRange>();
    }

    int instruction_id = instructions_[instruction_index];
    return get_parameter_ranges_for_instruction(instruction_id);
}

std::vector<uint8_t> Instrument::get_instruction_parameter_types(uint32_t instruction_index) const
{
    if (instruction_index >= instructions_.size())
    {
        return std::vector<uint8_t>();
    }

    int instruction_id = instructions_[instruction_index];
    return get_parameter_types_for_instruction(instruction_id);
}

std::vector<ParameterEnum> Instrument::get_instruction_parameter_enums(uint32_t instruction_index) const
{
    if (instruction_index >= instructions_.size())
    {
        return std::vector<ParameterEnum>();
    }

    int instruction_id = instructions_[instruction_index];
    return get_parameter_enums_for_instruction(instruction_id);
}

std::string Instrument::get_instruction_name(uint32_t instruction_index) const
{
    if (instruction_index >= instructions_.size())
    {
        return "UNKNOWN";
    }

    int instruction_id = instructions_[instruction_index];
    return get_instruction_name_by_id(instruction_id);
}

void Instrument::update_parameter(uint32_t instruction_index, uint32_t param_index, uint32_t value)
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
            else if (param_types[param_index] == static_cast<uint8_t>(ParameterType::ENUM))
            {
                // Update enum parameter (stored as uint8_t value)
                if (ptr_idx < parameters_[instruction_index].size())
                {
                    *(parameters_[instruction_index][ptr_idx]) = static_cast<uint8_t>(value & 0xFF);
                    DEBUG_LOG("Updated Instrument " << id_ << " instruction " << instruction_index
                                                    << " param " << param_index << " (enum) to " << static_cast<int>(value & 0xFF));
                }
            }
        }
    }
}

void Instrument::update_parameter_with_string(uint32_t instruction_index, uint32_t param_index, const std::string &value)
{
    if (instruction_index < parameters_.size())
    {
        int instruction_id = instructions_[instruction_index];
        std::vector<uint8_t> param_types = get_parameter_types_for_instruction(instruction_id);
        std::vector<ParameterEnum> param_enums = get_parameter_enums_for_instruction(instruction_id);

        if (param_index < param_types.size())
        {
            if (param_types[param_index] == static_cast<uint8_t>(ParameterType::ENUM))
            {
                // For enum parameters, convert string to uint8_t value
                if (param_index < param_enums.size() && !param_enums[param_index].values.empty())
                {
                    uint8_t enum_value = param_enums[param_index].get_value(value);
                    update_parameter(instruction_index, param_index, enum_value);
                }
            }
            else
            {
                // For non-enum parameters, convert string to number
                try
                {
                    uint32_t numeric_value = std::stoul(value);
                    update_parameter(instruction_index, param_index, numeric_value);
                }
                catch (const std::exception &)
                {
                    // Invalid number, ignore
                }
            }
        }
    }
}

std::vector<float> Instrument::render_note(uint32_t note_num)
{
    int num_notes = 10;
    int num_samples = SAMPLES_PER_NOTE * num_notes;
    DEBUG_LOG("Instrument " << id_ << " rendering " << num_samples << " samples for note " << note_num);
    std::vector<float> output(num_samples);

    debug_start_instrument_note(id_, note_num);

    // Render samples with hold and release phases
    for (int i = 0; i < num_samples; i++)
    {
        uint8_t release = (i >= SAMPLES_PER_NOTE * (num_notes - 2)) ? 1 : 0;
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

void Instrument::load_instructions_and_parameters()
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

void Instrument::load_parameters_for_instructions()
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
            uint32_t num_params = get_instruction_memory_size(temp_instr_ptr[0]);
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

uint32_t Instrument::get_instruction_param_count(int instruction_id) const
{
    switch (instruction_id)
    {
    case ENVELOPE_ID:
        return 5;
    case OSCILLATOR_ID:
        return 8;
    case STOREVAL_ID:
        return 2; // Changed from 3 to 2: Amount + merged Destination
    case FILTER_ID:
        return 3; // Frequency, Resonance, Type
    case OPERATION_ID:
        return 1;
    case OUTPUT_ID:
        return 1;
    case PANNING_ID:
        return 1; // Assuming 1 parameter each
    default:
        return 0;
    }
}

uint32_t Instrument::get_instruction_memory_size(int instruction_id) const
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
        return 3; // Frequency (1 byte) + Resonance (1 byte) + Type (1 byte) = 3 bytes total
    case PANNING_ID:
        return 1; // 1 uint8 parameter each
    default:
        return 0;
    }
}

std::string Instrument::get_instruction_name_by_id(int instruction_id) const
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

std::vector<std::string> Instrument::get_parameter_names_for_instruction(int instruction_id) const
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
        return {"Frequency", "Resonance", "Type"};
    case PANNING_ID:
        return {"Position"};
    case ACCUMULATE_ID:
        return {}; // No parameters
    default:
        return {};
    }
}

std::vector<ParameterRange> Instrument::get_parameter_ranges_for_instruction(int instruction_id) const
{
    switch (instruction_id)
    {
    case ENVELOPE_ID:
        // Attack, Decay, Sustain, Release, Gain (all default step=1)
        return {ParameterRange(0, 128), ParameterRange(0, 128), ParameterRange(0, 128),
                ParameterRange(0, 128), ParameterRange(0, 128)};
    case OSCILLATOR_ID:
        // Transpose, Detune, Phase, Gates, Color, Shape, Gain, Type (some with custom steps)
        return {ParameterRange(0, 128), ParameterRange(0, 128), ParameterRange(0, 128),
                ParameterRange(0, 128), ParameterRange(0, 128), ParameterRange(0, 128),
                ParameterRange(0, 128), ParameterRange(0, 7)};
    case STOREVAL_ID:
        // Amount (step=1), Destination (uint16, larger step for coarse control)
        return {ParameterRange(0, 128), ParameterRange(0, 65535, 4)};
    case OPERATION_ID:
        // Operand (step=1)
        return {ParameterRange(0, 15)};
    case OUTPUT_ID:
        // Gain (step=1)
        return {ParameterRange(0, 128)};
    case FILTER_ID:
        // Frequency (step=1), Resonance (step=1), Type (enum)
        return {ParameterRange(0, 128), ParameterRange(0, 128), ParameterRange(0, 2)};
    case PANNING_ID:
        // Position (-64 to +63, but we'll map 0-127, step=1)
        return {ParameterRange(0, 127)};
    case ACCUMULATE_ID:
        return {}; // No parameters
    default:
        return {};
    }
}

std::vector<uint8_t> Instrument::get_parameter_types_for_instruction(int instruction_id) const
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
        // Transpose, Detune, Phase, Gates, Color, Shape, Gain, Type (Type is enum)
        return {static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::ENUM)};
    case STOREVAL_ID:
        // Amount (uint8), Destination (uint16)
        return {static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::UINT16)};
    case OPERATION_ID:
        // Operand - enum type
        return {static_cast<uint8_t>(ParameterType::ENUM)};
    case OUTPUT_ID:
        // Gain - uint8_t for now
        return {static_cast<uint8_t>(ParameterType::UINT8)};
    case FILTER_ID:
        // Frequency, Resonance - uint8_t, Type - enum
        return {static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::UINT8),
                static_cast<uint8_t>(ParameterType::ENUM)};
    case PANNING_ID:
        // Position - uint8_t for now
        return {static_cast<uint8_t>(ParameterType::UINT8)};
    case ACCUMULATE_ID:
        return {}; // No parameters
    default:
        return {};
    }
}

std::vector<ParameterEnum> Instrument::get_parameter_enums_for_instruction(int instruction_id) const
{
    switch (instruction_id)
    {
    case OSCILLATOR_ID:
        // Return enum definitions for each parameter (empty for non-enum parameters)
        return {
            ParameterEnum({}), // Transpose - not enum
            ParameterEnum({}), // Detune - not enum
            ParameterEnum({}), // Phase - not enum
            ParameterEnum({}), // Gates - not enum
            ParameterEnum({}), // Color - not enum
            ParameterEnum({}), // Shape - not enum
            ParameterEnum({}), // Gain - not enum
            ParameterEnum({    // Type - enum (using actual bit flag values from defines.h)
                           EnumValue(OSCILLATOR_SINE, "Sine"),
                           EnumValue(OSCILLATOR_SQUARE, "Square"),
                           EnumValue(OSCILLATOR_SAW, "Sawtooth"),
                           EnumValue(OSCILLATOR_TRIANGLE, "Triangle"),
                           EnumValue(OSCILLATOR_NOISE, "Noise"),
                           EnumValue(OSCILLATOR_SINE + OSCILLATOR_LFO, "Sine+LFO"),
                           EnumValue(OSCILLATOR_SQUARE + OSCILLATOR_LFO, "Square+LFO"),
                           EnumValue(OSCILLATOR_SAW + OSCILLATOR_LFO, "Sawtooth+LFO"),
                           EnumValue(OSCILLATOR_TRIANGLE + OSCILLATOR_LFO, "Triangle+LFO"),
                           EnumValue(OSCILLATOR_NOISE + OSCILLATOR_LFO, "Noise+LFO")})};
    case OPERATION_ID:
        return {
            ParameterEnum({// Operand - enum (using operator values from defines.h)
                           EnumValue(OPERATOR_MUL, "Multiply"),
                           EnumValue(OPERATOR_MULP, "Multiply and Pop")})};
    case FILTER_ID:
        return {
            ParameterEnum({}), // Frequency - not enum
            ParameterEnum({}), // Resonance - not enum
            ParameterEnum({    // Type - enum
                           EnumValue(FILTER_LOWPASS, "Low Pass"),
                           EnumValue(FILTER_HIGHPASS, "High Pass"),
                           EnumValue(FILTER_BANDSTOP, "Band Stop"),
                           EnumValue(FILTER_BANDPASS, "Band Pass"),
                           EnumValue(FILTER_ALLPASS, "All Pass"),
                           EnumValue(FILTER_PEAK, "Peak")})};
    default:
        return {};
    }
}