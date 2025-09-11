// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#ifdef __APPLE__
#include <SDL2/SDL.h>
#else
#include <SDL/SDL.h>
#endif
#include <cmath>

#define NUM_TONES 6

bool on[NUM_TONES];
bool lfoOn;

float phase[NUM_TONES];
float modPhase = 0.0f;
float modFrequency = 5.0f;

typedef struct
{
    float frequency;
    float amplitude;
} Tone;

enum Waveform {
    SINE,
    SQUARE
};
float
Generator(float frequency,
          float amplitude,
          float& phase,
          Waveform waveform)
{
    float ret = 0.0f;

    switch(waveform) {
    case SINE:
        ret = std::sin(phase) * amplitude;
        break;
    case SQUARE:
        if(std::sin(phase) > 0)
            ret = amplitude;
        else
            ret = -amplitude;
        break;
    }
    phase += 2 * M_PI * frequency / 44100.0f;

    return ret;
}

void AudioCallback(void* userdata, 
                   Uint8 *stream, 
                   int len)
{
    // Play 440Hz
    // 2pi * 440 [amp/s]
    // 2pi * 440 / 44100 [amp/sample]
    
    const float BaseTone = 440.0f;
    Tone tones[NUM_TONES] = {
        {BaseTone * 1.0f * 1.0f,   1.0f},
        {BaseTone * 1.0f * 1.26f,  0.5f},
        {BaseTone * 1.0f * 1.498f, 0.5f},
        {BaseTone * 2.0f * 1.0f,   0.3f},
        {BaseTone * 2.0f * 1.26f,  0.3f},
        {BaseTone * 2.0f * 1.498f, 0.3f},
    };

    Sint16* samples = reinterpret_cast<Sint16*>(stream);
    int numSamples = len / 2;

    for(int i = 0; i < numSamples; i++) {
        float sample = 0.0f;
        float ampSum = 0.0f;
        for(int j = 0; j < NUM_TONES; j++) {
            float val = Generator(tones[j].frequency, tones[j].amplitude, 
                                  phase[j], SINE);
            if(on[j]) {
                sample += val;
                ampSum += tones[j].amplitude;
            }
        }
        sample *= (32767.0f / (ampSum));

        // LFO
        float lfo = Generator(modFrequency, 1.0f, modPhase, SINE);
        if(lfoOn)
            sample *= lfo;
        //sample /= 2.0f;
        samples[i] = static_cast<Sint16>(sample);
    }
}


int
main(void)
{
    int ret;

    for(int i = 0; i < NUM_TONES; i++) {
        on[i] = false;
        phase[i] = 0.0f;
    }
    on[0] = true;
    lfoOn = true;

    if((ret = SDL_Init(SDL_INIT_TIMER | SDL_INIT_VIDEO | SDL_INIT_AUDIO)) != 0) {
        printf("Could not initialize SDL\n");
    } else {
        // Init audio    
        SDL_AudioSpec desired;
        SDL_AudioSpec obtained;
        desired.freq = 44100; // 44kHz
        desired.format = AUDIO_S16SYS; // 16Bit
        desired.channels = 1; // Mono
        desired.samples = 4096; // 1024 samples per callback
        desired.callback = AudioCallback;
        desired.userdata = 0;
        if((ret = SDL_OpenAudio(&desired, &obtained)) != 0) {
            printf("Could not initialize Audio\n");
        } else {
#ifdef __APPLE__
            SDL_Window *videoSurface = SDL_CreateWindow(NULL, 0, 0, 1024, 768, SDL_WINDOW_OPENGL);
            SDL_GL_CreateContext(videoSurface);
#else
            SDL_Surface *videoSurface = SDL_SetVideoMode(800, 600, 32,
                                                         SDL_ANYFORMAT | SDL_HWACCEL | SDL_HWSURFACE);
#endif
            if(videoSurface == 0) {
                printf("Could not initialize Video\n");
                ret = -1;
            } else {
                // Start audio
                SDL_PauseAudio(0);

                SDL_Event event;
                bool quit = false;
                while(!quit) {
                    while(SDL_PollEvent(&event)) {
                        switch(event.type) {
                        case SDL_KEYDOWN:
                            switch(event.key.keysym.sym) {
                            case SDLK_ESCAPE:
                                quit = true;
                                break;
                            case SDLK_1:
                            case SDLK_2:
                            case SDLK_3:
                            case SDLK_4:
                            case SDLK_5:
                            case SDLK_6:
                                on[event.key.keysym.sym - SDLK_1] = 
                                    !on[event.key.keysym.sym - SDLK_1];
                                break;
                            case SDLK_l:
                                lfoOn = !lfoOn;
                                break;
                            case SDLK_RIGHT:
                                modFrequency += 0.1f;
                                break;
                            case SDLK_LEFT:
                                modFrequency -= 0.1f;
                                break;
                            }
                            break;
                        }
                    }
                }
            }
        }
   }

    SDL_Quit();
    return 0;
}
