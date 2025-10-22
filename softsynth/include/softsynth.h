#ifndef SOFT_SYNTH_H
#define SOFT_SYNTH_H

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
    void output_function(void);
    void process_stack(void);
    extern void (*instrument_instructions_lookup[256])(void);
    void new_instrument_note(void);

#ifdef __cplusplus
}
#endif

#endif // SOFT_SYNTH_H