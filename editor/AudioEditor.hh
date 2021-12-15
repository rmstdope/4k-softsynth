// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#ifndef AUDIO_EDITOR_H
#define AUDIO_EDITOR_H

#ifdef WIN32
#include <windows.h>
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <fstream>
#include <vector>
#ifdef WIN32
#include <SDL.h>
#else
#include <SDL/SDL.h>
#endif
#include <GL/gl.h>
#include <glTexFont.h>
#include "softsynth.h"
#include "Display.hh"
#include "PatternEdit.hh"
#include "TrackEdit.hh"
#include "InstrumentEdit.hh"

class AudioEditor
{
public:
    /// Constructor
    AudioEditor();
    /// Destructor
    ~AudioEditor();
    /// Initialize the class
    bool Initialize();
    /// Callback for filling audio buffers
    void AudioCallback(Uint8 *stream, int len);
    /// Mainloop of editor
    void MainLoop(void);
private:
    enum Constants {
        MAX_NUM_INSTRUMENTS = 20,
        NUM_INSTRUMENTS = 10,
        NUM_PATTERNS = 20
    };
    // Edit modes
    enum EditMode {
        MODE_INSTRUMENT = 0,
        MODE_PATTERN,
        MODE_TRACK,
        NUM_MODES
    };
    // Actions
    enum Actions {
        SAVE = 0,
        LOAD,
        NUM_ACTIONS
    };
    void DrawPixel(Sint32 x, Sint32 y, Uint8 r, Uint8 g, Uint8 b);

    /// Video surface
    SDL_Surface* mVideoSurface;

    EditMode mCurrentMode;
    EditBase* mEditMode[NUM_MODES];
};

#endif
