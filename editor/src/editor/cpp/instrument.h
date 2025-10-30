/*
 * Instrument class for 4K Softsynth
 * Represents a single synthesizer instrument with parameters and rendering capabilities
 */

#pragma once

#include <vector>
#include <string>
#include <cstdint>

// Forward declarations
struct ParameterRange;
struct ParameterEnum;

class Instrument
{
public:
    Instrument(uint32_t instrument_id);

    uint32_t get_id() const { return id_; }

    const std::vector<int> &get_instructions() const { return instructions_; }

    const std::vector<std::vector<uint8_t *>> &get_parameters() const { return parameters_; }

    std::vector<uint8_t> get_instruction_parameters(uint32_t instruction_index) const;

    std::vector<uint32_t> get_instruction_parameters_full(uint32_t instruction_index) const;

    std::vector<std::string> get_instruction_parameters_as_strings(uint32_t instruction_index) const;

    std::vector<std::string> get_instruction_parameter_names(uint32_t instruction_index) const;

    std::vector<ParameterRange> get_instruction_parameter_ranges(uint32_t instruction_index) const;

    std::vector<uint8_t> get_instruction_parameter_types(uint32_t instruction_index) const;

    std::vector<ParameterEnum> get_instruction_parameter_enums(uint32_t instruction_index) const;

    std::string get_instruction_name(uint32_t instruction_index) const;

    void update_parameter(uint32_t instruction_index, uint32_t param_index, uint32_t value);

    void update_parameter_with_string(uint32_t instruction_index, uint32_t param_index, const std::string &value);

    std::vector<float> render_note(uint32_t note_num);

private:
    uint32_t id_;
    std::vector<int> instructions_;
    std::vector<std::vector<uint8_t *>> parameters_; // Store pointers to actual parameter locations

    void load_instructions_and_parameters();

    void load_parameters_for_instructions();

    uint32_t get_instruction_param_count(int instruction_id) const;

    uint32_t get_instruction_memory_size(int instruction_id) const;

    std::string get_instruction_name_by_id(int instruction_id) const;

    std::vector<std::string> get_parameter_names_for_instruction(int instruction_id) const;

    std::vector<ParameterRange> get_parameter_ranges_for_instruction(int instruction_id) const;

    std::vector<uint8_t> get_parameter_types_for_instruction(int instruction_id) const;

    std::vector<ParameterEnum> get_parameter_enums_for_instruction(int instruction_id) const;
};