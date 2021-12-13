// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#ifndef EDIT_BASE_H
#define EDIT_BASE_H

#include <string>
#include <fstream>
#include <SDL/SDL.h>

#include "softsynth.h"

class EditBase
{
public:
    /// Constructor
    EditBase();
    /// Toggle help on and off
    void ToggleHelp(void);
    /// Check if pattern is playing
    bool IsPlaying(void) const;
    /// Audio callback for playing patterns
    virtual void AudioCallback(Uint8 *stream, int len) = 0;
    /// Main loop for edit mode
    void ProcessEvents(SDL_Event* events, int numEvents);
    /// Check if user wants to quit
    bool ShouldQuit(void) const;
    /// Stop edit mode
    virtual void StopMode(void) = 0;
    /// Start edit mode
    virtual void StartMode(void) = 0;
protected:
    enum Constants {
        FILENAME_LENGTH = 20,
        NUM_KEYS = 28
    };
    enum Dialogue {
        NO_DIALOGUE = 0,
        LOAD_DIALOGUE,
        SAVE_DIALOGUE
    };

    // Present rendered scene
    void Present(void);
    // Clear screen
    void Clear(void);
    // Set redraw flag
    void Redraw(void);
    /// If ok, decrease selection value
    virtual void DecSelection(void) = 0;
    /// If ok, increase selection value
    virtual void IncSelection(void) = 0;
    /// Get the name of a note
    const char* const GetNote(Sint8 note);
    /// Get the name of a pattern
    std::string GetPattern(Sint8 pattern);
    /// Get the waveform of a generator function
    WaveForms GetWaveform(WaveformFunc ptr);
    /// Get a pointer to a generator function
    WaveformFunc GetWaveformFunc(WaveForms);
    /// Draw the help screen
    void DrawHelp(std::string* strings, int num);
    /// Perform pattern edit change
    virtual void Change(int sign, bool moveFast) = 0;
    /// Act on key pressed
    virtual void KeyPressed(SDLKey key, SDLMod mod) = 0;
    /// Act on key unpressed
    virtual void KeyUnpressed(SDLKey key, SDLMod mod);
    /// Draw the screen
    virtual void Draw(void) = 0;
    /// Draw dialogue info
    void DrawDialogue(void);
    /// Start save dialogue
    void Save(void);
    /// Start load dialogue
    void Load(void);
    /// Write data to file
    virtual void WriteToFile(std::ofstream& fil) = 0;
    /// Read data to file
    virtual void ReadFromFile(std::ifstream& fil) = 0;
    /// Get extension
    virtual std::string GetExtension(void) const = 0;

    static const SDLKey mNoteKeys[NUM_KEYS];
    bool mHelp;
    bool mPlaying;
private:
    void PerformSave(void);
    void PerformLoad(void);

    bool mRedraw;
    bool mQuit;
    Dialogue mDialogue;
    std::string mFilename;
};

#endif
