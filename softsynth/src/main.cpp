#define GL_SILENCE_DEPRECATION 1

#include <SDL2/SDL.h>
// #include <OpenGL/OpenGL.h>
// #include <OpenGL/glu.h>
#include "softsynth.h"

// extern "C" void softsynth_init(void);
// extern "C" void softsynth_playback(void *userdata, Uint8 *stream, int len);

char data[64];

// #define FULLSCREEN
int main(void)
{
    dope4ks_render(NULL, (Uint8 *)data, 64);

    SDL_Init(SDL_INIT_VIDEO);
    SDL_Window *window = SDL_CreateWindow(NULL, 0, 0, 1024, 768, SDL_WINDOW_OPENGL);
    SDL_AudioSpec desiredSpec;
    desiredSpec.freq = 44100;
    desiredSpec.format = AUDIO_S16LSB;
    desiredSpec.channels = 1;
    desiredSpec.samples = 4096;
    desiredSpec.callback = dope4ks_render;
    SDL_OpenAudio(&desiredSpec, NULL);
    SDL_PauseAudio(0);

    while (!SDL_HasEvent(SDL_QUIT))
    {
        SDL_PumpEvents();
    }
    return 0;
}