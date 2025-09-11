#ifndef SOFTSYNTH_H
#define SOFTSYNTH_H

#define c1 0
#define C1 1
#define d1 2
#define D1 3
#define e1 4
#define f1 5
#define F1 6
#define g1 7
#define G1 8
#define a1 9
#define A1 10
#define b1 11
#define c2 12
#define C2 13
#define d2 14
#define D2 15
#define e2 16
#define f2 17
#define F2 18
#define g2 19
#define G2 20
#define a2 21
#define A2 22
#define b2 23
#define c3 24
#define C3 25
#define d3 26
#define D3 27
#define e3 28
#define f3 29
#define F3 30
#define g3 31
#define G3 32
#define a3 33
#define A3 34
#define b3 35
#define c4 36
#define C4 37
#define d4 38
#define D4 39
#define e4 40
#define f4 41
#define F4 42
#define g4 43
#define G4 44
#define a4 45
#define A4 46
#define b4 47
#define c5 48
#define C5 49
#define d5 50
#define D5 51
#define e5 52
#define f5 53
#define F5 54
#define g5 55
#define G5 56
#define a5 57
#define A5 58
#define b5 59
#define c6 60
#define C6 61
#define d6 62
#define D6 63
#define e6 64
#define f6 65
#define F6 66
#define g6 67
#define G6 68
#define a6 69
#define A6 70
#define b6 71

#define BEATS_PER_MINUTE 125
#define NOTES_PER_BEAT 4
#define ROW_TICKS (60 * 44100 / (BEATS_PER_MINUTE * NOTES_PER_BEAT))

#define END_PATTERN -2
#define END_TRACK -2
#define LOOP_TRACK -3
#define STOP -4
#define ECHO_ON -5
#define ECHO_OFF -6
#define HOLD_5 -7
#define HOLD_4 -8
#define HOLD_3 -9
#define HOLD_2 -10
#define HOLD_1 -11

enum WaveForms {
  SINE = 0,
  NOISE,
  SQUARE,
  SAWTOOTH,
  NUM_WAVEFORMS
};

typedef void (*WaveformFunc)(void);

#ifdef __APPLE__
typedef struct
{
  WaveformFunc waveForm;
  float attack;
  float decay;
  float sustain;
  float release;
  float modulation;
  float sweep;
} InstrumentStruct;
#else
typedef struct 
{
    WaveformFunc waveForm;
    Sint32 attack;
    Sint32 decay;
    float sustain;
    Sint32 release;
    float modulation;
    float sweep;
} InstrumentStruct;
#endif

// Assembler functions
extern "C" void softsynth_init(void);
extern "C" void softsynth_play(void* userdata, 
                               Uint8 *stream, 
                               int len);
extern "C" void softsynth_regenerate_samples(void);

extern "C" void start_instrument(Uint32 instrument,
                                 Uint32 note);
extern "C" int get_instrument_value_c(Uint32 instrument);

extern "C" void get_sine_waveform(void);
extern "C" void get_noise_waveform(void);
extern "C" void get_square_waveform(void);
extern "C" void get_sawtooth_waveform(void);

// Assembler variables
extern "C" float instrument_hold[];
extern "C" Uint32 instrument_ticks[];
extern "C" InstrumentStruct instrument_definition[];
extern "C" Sint8* pattern_list[];
extern "C" Sint32 pattern_index[];
extern "C" Sint8* track_list[];
extern "C" Sint32 track_index[];
extern "C" Uint32 ticks;

#endif
