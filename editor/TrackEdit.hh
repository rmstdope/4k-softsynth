// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#ifndef TRACK_EDIT
#define TRACK_EDIT

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
#include "EditBase.hh"

class PatternEdit;

class TrackEdit :
    public EditBase
{
public:
    /// Constructor
    TrackEdit(PatternEdit* pEdit, int numInstruments, int numPatterns);
    /// Destructor
    ~TrackEdit();
    /// Draw the track display
    void Draw(void);
    /// Stop playing song
    void StopSong(void);
    /// Perform track edit change
    void Change(int sign, bool moveFast);
    /// Audio callback for playing tracks
    void AudioCallback(Uint8 *stream, int len);
    /// If ok, decrease selection value
    void DecSelection(void);
    /// If ok, increase selection value
    void IncSelection(void);
    /// Act on key pressed
    void KeyPressed(SDL_Keycode key, Uint16 mod);
    /// Stop edit mode
    void StopMode(void);
    /// Start edit mode
    void StartMode(void);
    /// Write data to file
    void WriteToFile(std::ofstream& fil);
    /// Read data to file
    void ReadFromFile(std::ifstream& fil);
    /// Get extension name
    std::string GetExtension(void) const { return "track"; }
private:
    enum Constants {
        MAX_TRACK_LENGTH = 1024,
        MAX_NUM_INSTRUMENTS = 20
    };
    enum TrackChoices {
        TRACK_DELIMITER_1 = 0,
        TRACK_SAVE,
        TRACK_LOAD,
        TRACK_SELECTIONS
    };
    enum Window {
        WINDOW_MENU = 0,
        WINDOW_TRACK
    };
    /// Start playing song
    void StartSong(void);
    /// Fetch track data from asm data
    void FetchTracks(void);
    /// Store track data to asm data
    void StoreTracks(void);
    /// Mute/unmute intrument
    void Mute(int instrument, bool mute);
    /// Check if instrument is muted
    bool IsMuted(int instrument) const;

    int mNumInstruments;
    int mNumPatterns;
    int mInstrumentNum;

    int mMenuSelection;
    int mTrackSelection;
    int mTrackNum;
    Sint8 mTrackData[MAX_NUM_INSTRUMENTS][MAX_TRACK_LENGTH];
    Sint8 mMutedTrack[2];
    int mTrackLength[MAX_NUM_INSTRUMENTS];

    bool mInstrumentMuted[MAX_NUM_INSTRUMENTS];
    bool mLastMute;

    Window mActiveWindow;

    PatternEdit* mPatternEdit;
};

#endif
