// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#ifndef PATTERN_EDIT
#define PATTERN_EDIT

#include <SDL/SDL.h>
#include "EditBase.hh"

class PatternEdit :
    public EditBase
{
public:
    /// Constructor
    PatternEdit(int numInstruments, int numPatterns);
    /// Destructor
    ~PatternEdit();
    /// Draw the pattern display
    void Draw(void);
    /// Stop playing single pattern
    void StopPattern(void);
    /// Perform pattern edit change
    void Change(int sign, bool moveFast);
    /// Audio callback for playing patterns
    void AudioCallback(Uint8 *stream, int len);
    /// If ok, decrease selection value
    void DecSelection(void);
    /// If ok, increase selection value
    void IncSelection(void);
    /// Act on key pressed
    void KeyPressed(SDLKey key, SDLMod mod);
    /// Stop edit mode
    void StopMode(void);
    /// Start edit mode
    void StartMode(void);
    /// Write data to file
    void WriteToFile(std::ofstream& fil);
    void WriteToFile(std::ofstream& fil, int p = -1);
    /// Read data to file
    void ReadFromFile(std::ifstream& fil);
    void ReadFromFile(std::ifstream& fil, int p = -1);
    /// Get extension name
    std::string GetExtension(void) const { return "pattern"; }

    void Debug(void);
private:
    enum Constants {
        MAX_PATTERN_LENGTH = 64,
        MAX_NUM_PATTERNS = 255
    };
    enum PatternChoice {
        PATTERN_NUM = 0,
        PATTERN_INSTRUMENT,
        PATTERN_DELIMITER_1,
        PATTERN_SAVE,
        PATTERN_LOAD,
        PATTERN_SELECTIONS
    };
    enum Window {
        WINDOW_MENU = 0,
        WINDOW_PATTERN
    };
    /// Start playing single pattern
    void StartPattern(void);
    /// Fetch pattern data from asm data
    void FetchPatterns(void);
    /// Store pattern data pointer into asm data
    void StorePatterns(void);

    int mNumInstruments;
    int mInstrumentNum;

    int mMenuSelection;
    int mPatternSelection;
    int mNumPatterns;
    int mPatternNum;
    Sint8 mPatternData[MAX_NUM_PATTERNS][MAX_PATTERN_LENGTH];
    Sint8 mPatternTrack[2];
    Sint8 mMutedTrack[2];
    int mPatternLength[MAX_NUM_PATTERNS];

    Window mActiveWindow;
};

#endif
