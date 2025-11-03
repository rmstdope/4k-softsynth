#ifndef SOFT_SYNTH_H
#define SOFT_SYNTH_H

#include "defines.h"

#ifdef __cplusplus
extern "C"
{
#endif

    void dope4ks_render(void *userdata,
                        unsigned char *stream,
                        int len);
    void transform_values(void);
    extern float transformed_parameters[16];
    void envelope_function(void);
    void storeval_function(void);
    void oscillator_function(void);
    void filter_function(void);
    void output_function(void);
    void accumulate_function(void);
    void process_stack(void);
    extern void (*instrument_instructions_lookup[256])(void);
    void new_instrument_note(void);
    void cosine_waveform(void);
    void pwr(void);

#ifdef DEBUG
    void debug_start_instrument_note(uint8_t instrument, uint8_t note);
    void debug_next_instrument_sample(uint8_t instrument, float *sample, uint8_t release);
    void debug_setup_sx_registers(void);
    extern uint32_t synth_data[];
    extern uint8_t instrument_instructions[];
    extern uint8_t instrument_parameters[];
#endif // DEBUG

#ifdef __cplusplus
}
#endif

#endif // SOFT_SYNTH_H