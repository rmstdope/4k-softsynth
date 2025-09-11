// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#ifndef INSTRUMENT_EDIT
#define INSTRUMENT_EDIT

#ifdef WIN32
#include <windows.h>
#endif
#ifdef WIN32
#include <SDL.h>
#elif __APPLE__
#include <SDL2/SDL.h>
#else
#include <SDL/SDL.h>
#endif
#include "Display.hh"
#include "EditBase.hh"

class InstrumentEdit :
    public EditBase
{
public:
    /// Constructor
    InstrumentEdit(int numInstruments);
    /// Destructor
    ~InstrumentEdit();
    /// Draw the pattern display
    void Draw(void);
    /// Stop playing single pattern
    void StopInstrument(void);
    /// Perform pattern edit change
    void Change(int sign, bool moveFast);
    /// Audio callback for playing patterns
    void AudioCallback(Uint8 *stream, int len);
    /// If ok, decrease selection value
    void DecSelection(void);
    /// If ok, increase selection value
    void IncSelection(void);
    /// Act on key pressed
    void KeyPressed(SDL_Keycode key, Uint16 mod);
    /// Act on key unpressed
    void KeyUnpressed(SDL_Keycode key, Uint16 mod);
    /// Stop edit mode
    void StopMode(void);
    /// Start edit mode
    void StartMode(void);
    /// Write data to file
    void WriteToFile(std::ofstream& fil);
    /// Read data to file
    void ReadFromFile(std::ifstream& fil);
    /// Get extension name
    std::string GetExtension(void) const { return "instrument"; }
private:
    enum Constants {
        MAX_NUM_INSTRUMENTS = 20
    };
    enum InstrumentChoices {
        INSTRUMENT_NUM = 0,
        INSTRUMENT_WAVEFORM,
        INSTRUMENT_ATTACK,
        INSTRUMENT_DECAY,
        INSTRUMENT_SUSTAIN,
        INSTRUMENT_RELEASE,
        INSTRUMENT_SWEEP,
        INSTRUMENT_MODULATION,
        INSTRUMENT_DELIMITER_1,
        INSTRUMENT_SAVE,
        INSTRUMENT_LOAD,
        INSTRUMENT_SELECTIONS
    };
    enum Window {
        WINDOW_MENU = 0,
        WINDOW_SAVE,
        WINDOW_LOAD
    };
    /// Start playing single pattern
    void StartInstrument(void);
    /// Get display data for instrument
    void GetDisplayData(void);

    int mNumInstruments;
    Uint32 mInstrumentPositionTick;
    int mInstrumentNum;
    int mInstrumentSelection;

    int mAction;

    SDL_Keycode mLastKey;

    Window mActiveWindow;

    Sint32 mDisplayData[Display::SCREEN_WIDTH];
};

#endif
