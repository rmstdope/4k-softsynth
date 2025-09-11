// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#define GL_SILENCE_DEPRECATION 1
#include "AudioEditor.hh"

void AudioCallback(void *userdata,
                   Uint8 *stream,
                   int len)
{
    reinterpret_cast<AudioEditor *>(userdata)->AudioCallback(stream, len);
}

AudioEditor::AudioEditor() : mVideoSurface(0),
                             mCurrentMode(MODE_INSTRUMENT)
{
}

AudioEditor::~AudioEditor()
{
    // Delete edit modes
    for (int i = 0; i < NUM_MODES; i++)
        delete mEditMode[i];

    // Clean up SDL
    SDL_Quit();
}

bool AudioEditor::Initialize()
{
    int ret;

    // Init SDL
    if ((ret = SDL_Init(SDL_INIT_TIMER | SDL_INIT_VIDEO | SDL_INIT_AUDIO)) != 0)
    {
        printf("Could not initialize SDL\n");
    }
    else
    {

        // Init audio
        SDL_AudioSpec desired;
        SDL_AudioSpec obtained;
        desired.freq = 44100;          // 44kHz
        desired.format = AUDIO_S16SYS; // 16Bit
        desired.channels = 1;          // Mono
        desired.samples = 4096;        // 1024 samples per callback
        desired.callback = ::AudioCallback;
        desired.userdata = this;
        if ((ret = SDL_OpenAudio(&desired, &obtained)) != 0)
        {
            printf("Could not initialize Audio\n");
        }
        else
        {

            // Use at least 5 bits of Red
            SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8);
            // Use at least 5 bits of Green
            SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8);
            // Use at least 5 bits of Blue
            SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8);
            // Use at least 16 bits for the depth buffer
            SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 16);
            // Enable double buffering
            SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);

            // Init video
#ifdef __APPLE__
            // mVideoSurface = SDL_CreateWindow(NULL, 0, 0, 0, 0, SDL_WINDOW_OPENGL | SDL_WINDOW_FULLSCREEN_DESKTOP);
            mVideoSurface = SDL_CreateWindow(NULL, 0, 0, Display::SCREEN_WIDTH, Display::SCREEN_HEIGHT, SDL_WINDOW_OPENGL);
            SDL_GL_CreateContext(mVideoSurface);
#else
            mVideoSurface =
                SDL_SetVideoMode(Display::SCREEN_WIDTH,
                                 Display::SCREEN_HEIGHT, 32,
                                 /*SDL_FULLSCREEN |*/ SDL_OPENGL |
                                     SDL_ANYFORMAT | SDL_HWACCEL | SDL_HWSURFACE);
#endif
            if (mVideoSurface == 0)
            {
                printf("Could not initialize Video\n");
                ret = -1;
            }
            else
            {
                glViewport(0, 0, Display::SCREEN_WIDTH,
                           Display::SCREEN_HEIGHT);
                glMatrixMode(GL_PROJECTION);
                glLoadIdentity();

                glOrtho(0.0f, Display::SCREEN_WIDTH,
                        Display::SCREEN_HEIGHT, 0.0f, -1.0f, 1.0f);

                glMatrixMode(GL_MODELVIEW);
                glLoadIdentity();

                glClearColor(0.0f, 0.0f, 0.0f, 0.5f);
                glClearDepth(1.0f);
                glDepthFunc(GL_LEQUAL);
                glEnable(GL_DEPTH_TEST);
                glShadeModel(GL_SMOOTH);
                glDisable(GL_CULL_FACE);
                glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);

                // Initialize softsynth
                printf("Initializing soft synth...");
                fflush(stdout);
                softsynth_init();
                printf("done\n");

                printf("Initializing glTexFont...");
                fflush(stdout);
                char font[] = "font.tga";
                if (fontLoad(font) != 1)
                {
                    printf("Error loading font \"%s\"\n", font);
                    fflush(stdout);
                    return 0;
                }
                printf("done\n");

                // Start audio
                SDL_PauseAudio(0);
            }
        }
    }

    // Create edit modes
    mEditMode[MODE_INSTRUMENT] = new InstrumentEdit(NUM_INSTRUMENTS);
    mEditMode[MODE_PATTERN] = new PatternEdit(NUM_INSTRUMENTS, NUM_PATTERNS);
    mEditMode[MODE_TRACK] = new TrackEdit(static_cast<PatternEdit *>(mEditMode[MODE_PATTERN]), NUM_INSTRUMENTS, NUM_PATTERNS);

    return ret == 0;
}

void AudioEditor::AudioCallback(Uint8 *stream,
                                int len)
{
    if (mEditMode[mCurrentMode]->IsPlaying())
        mEditMode[mCurrentMode]->AudioCallback(stream, len);
    else
        memset(stream, 0, len);
}

void AudioEditor::MainLoop(void)
{
    SDL_Event event;
    int numEvents;

    while (!mEditMode[mCurrentMode]->ShouldQuit())
    {
        // First check generic keys
        numEvents = SDL_PollEvent(&event);
        for (int i = 0; i < numEvents; i++)
        {
            switch (event.type)
            {
            case SDL_KEYDOWN:
                switch (event.key.keysym.sym)
                {
                case SDLK_F1:
                    mEditMode[mCurrentMode]->StopMode();
                    mCurrentMode = MODE_INSTRUMENT;
                    mEditMode[mCurrentMode]->StartMode();
                    break;
                case SDLK_F2:
                    mEditMode[mCurrentMode]->StopMode();
                    mCurrentMode = MODE_PATTERN;
                    mEditMode[mCurrentMode]->StartMode();
                    break;
                case SDLK_F3:
                    mEditMode[mCurrentMode]->StopMode();
                    mCurrentMode = MODE_TRACK;
                    mEditMode[mCurrentMode]->StartMode();
                    break;
                }
            }
        }

        // Do frame according to edit mode
        mEditMode[mCurrentMode]->SetVideoSurface(mVideoSurface);
        mEditMode[mCurrentMode]->ProcessEvents(&event, numEvents);
    }
}

// void
// AudioEditor::DrawPixel(Sint32 x,
//                        Sint32 y,
//                        Uint8 r,
//                        Uint8 g,
//                        Uint8 b)
// {
//     SDL_Rect rect;
//     rect.x = x;
//     rect.y = y;
//     rect.w = 1;
//     rect.h = 1;

//     Uint32 color = SDL_MapRGB(mVideoSurface->format, r, g, b);

//     SDL_FillRect(mVideoSurface, &rect, color);
//     SDL_UpdateRects(mVideoSurface, 1, &rect);  //This is the only new part
// }
