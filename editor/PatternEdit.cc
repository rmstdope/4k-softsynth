// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#include <glTexFont.h>
#include <string>

#include "PatternEdit.hh"
#include "Display.hh"
#include "softsynth.h"

PatternEdit::PatternEdit(int numInstruments, int numPatterns) :
    mNumInstruments(numInstruments),
    mInstrumentNum(0),
    mMenuSelection(0),
    mPatternSelection(0),
    mNumPatterns(numPatterns),
    mPatternNum(0),
    mActiveWindow(WINDOW_MENU)
{
    mMutedTrack[0] = 0;
    mMutedTrack[1] = LOOP_TRACK;

    mPatternTrack[0] = 0;
    mPatternTrack[1] = LOOP_TRACK;

    // Get patterns
    FetchPatterns();

    // Fix ASM patterns
    StorePatterns();
}

PatternEdit::~PatternEdit()
{
}

void
PatternEdit::AudioCallback(Uint8 *stream, 
                           int len)
{
    softsynth_play(0, stream, len);
}

void 
PatternEdit::StartPattern(void)
{
    mPatternTrack[0] = mPatternNum;
    
    for(int i = 0; i < mNumInstruments; i++) {
        track_index[i] = -1;
        if(i == mInstrumentNum) {
            track_list[i] = mPatternTrack;
        } else {
            track_list[i] = mMutedTrack;
        }
    }
    ticks = 0;

    mPlaying = true;
}

void 
PatternEdit::StopPattern(void)
{
    mPlaying = false;
}

void
PatternEdit::DecSelection(void)
{
    switch(mActiveWindow) {
    case WINDOW_MENU:
        if(mMenuSelection > 0)
            mMenuSelection--;
        break;
    case WINDOW_PATTERN:
        if(mPatternSelection > 0)
            mPatternSelection--;
        break;
    }
}

void
PatternEdit::IncSelection(void)
{
    switch(mActiveWindow) {
    case WINDOW_MENU:
        if(mMenuSelection < PATTERN_SELECTIONS - 1)
            mMenuSelection++;
    case WINDOW_PATTERN:
        if(mPatternSelection < mPatternLength[mPatternNum] - 2)
            mPatternSelection++;
        break;
    }
}

void
PatternEdit::KeyPressed(SDLKey key,
                        SDLMod mod)
{
    switch(key) {
    case SDLK_RETURN:
        if(mMenuSelection == PATTERN_SAVE) {
            Save();
        } else if(mMenuSelection == PATTERN_LOAD) {
            Load();
        }
        break;
    case SDLK_TAB:
        if(mActiveWindow == WINDOW_MENU)
            mActiveWindow = WINDOW_PATTERN;
        else
            mActiveWindow = WINDOW_MENU;
        break;
    case SDLK_SPACE:
        if(mPlaying)
            StopPattern();
        else
            StartPattern();
        break;
    }

    if(mActiveWindow == WINDOW_PATTERN) {
        switch(key) {
        case SDLK_BACKSPACE:
            mPatternData[mPatternNum][mPatternSelection] = 0;
            IncSelection();
            break;
        case SDLK_INSERT:
            if(mPatternLength[mPatternNum] <= MAX_PATTERN_LENGTH) {
                int len = mPatternLength[mPatternNum] - mPatternSelection;
                mPatternLength[mPatternNum]++;
                for(int i = 0; i < len; i++) {
                    mPatternData[mPatternNum][mPatternSelection - i + len] =
                        mPatternData[mPatternNum][mPatternSelection - i - 1 + len];
                }
                mPatternData[mPatternNum][mPatternSelection] = 0;
            }
            break;
        case SDLK_DELETE:
            if(mPatternLength[mPatternNum] > 2) {
                int len = mPatternLength[mPatternNum] - mPatternSelection - 1;
                for(int i = 0; i < len; i++) {
                    mPatternData[mPatternNum][mPatternSelection + i] = 
                        mPatternData[mPatternNum][mPatternSelection + 1 + i];
                }
                mPatternLength[mPatternNum]--;
                if(mPatternSelection >= mPatternLength[mPatternNum] - 1)
                    mPatternSelection = mPatternLength[mPatternNum] - 2;
            }
            break;
        case SDLK_KP_PLUS:
        case SDLK_PLUS:
            if(mPatternLength[mPatternNum] <= MAX_PATTERN_LENGTH) {
                mPatternData[mPatternNum][mPatternLength[mPatternNum] - 1] = 0;
                mPatternLength[mPatternNum]++;
                mPatternData[mPatternNum][mPatternLength[mPatternNum] - 1] = 
                    END_PATTERN;
            }
            break;
        case SDLK_KP_MINUS:
        case SDLK_MINUS:
            if(mPatternLength[mPatternNum] > 2) {
                mPatternLength[mPatternNum]--;
                mPatternData[mPatternNum][mPatternLength[mPatternNum] - 1] = 
                    END_PATTERN;
            }
            break;
        default:
            for(int i = 0; i < NUM_KEYS; i++) {
                int startNote = C3;
                if(mod & KMOD_LSHIFT)
                    startNote = C1;
                if(key == mNoteKeys[i]) {
                    mPatternData[mPatternNum][mPatternSelection] = startNote+i;
                    IncSelection();
                    break;
                }
            }
        }
    }
}

void
PatternEdit::Draw(void)
{
    char str[200];
    std::string text;

    // Draw pattern info
    fontSize(10);
    snprintf(str, 200, "Pattern %d", mPatternNum);
    fontDrawString(Display::SCREEN_WIDTH / 4, 
                   Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 4, 
                   str);
    for(size_t i = 0; i < (size_t)mPatternLength[mPatternNum]; i++) {
        fontSize(10);
        if(mActiveWindow == WINDOW_PATTERN &&
           mPatternSelection == i)
            fontColor(1, 0, 0);
        fontDrawString(Display::SCREEN_WIDTH / 4, 
                       Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 4 - 10 * (i + 1), 
                       GetNote(mPatternData[mPatternNum][i]));
    }
    
    // Draw pattern menu
    for(int i = 0; i < PATTERN_SELECTIONS; i++) {
        switch(i) {
        case PATTERN_NUM:
            snprintf(str, 200, "Pattern: %d", mPatternNum);
            break;
        case PATTERN_INSTRUMENT:
            snprintf(str, 200, "Instrument: %d", mInstrumentNum);
            break;
        case PATTERN_DELIMITER_1:
            snprintf(str, 200, "  ---  ");
            break;
        case PATTERN_SAVE:
            snprintf(str, 200, "Save Pattern");
            break;
        case PATTERN_LOAD:
            snprintf(str, 200, "Load Pattern");
            break;
        }
        
        // Draw Text
        fontSize(10);
        if(mActiveWindow == WINDOW_MENU && 
           mMenuSelection == i) {
            fontColor(1, 0, 0);
            text = std::string("-> ") + str;
        } else {
            fontColor(0.8f, 0.8f, 0.8f);
            text = str;
        }
        fontDrawString (0, Display::SCREEN_HEIGHT - 10 * (i + 1), text.c_str());
    }


    // Draw help?
    if(mHelp) {
        std::string helpStrings[] = {
            "Space      - Play/Stop pattern",
            "Tab        - Toggle menu/edit",
            "+          - Increase pattern length",
            "-          - Decrease pattern length",
            "Del        - Remove beat at current pos",
            "Ins        - Insert beat at current pos",
            "Right/Left - Inc/Dec note value",
            "a-z[+Shift]- Set note",
        };

        DrawHelp(helpStrings, sizeof(helpStrings) / sizeof(std::string));
    }
}

void
PatternEdit::Change(int sign,
                    bool moveFast)
{
    switch(mActiveWindow) {
    case WINDOW_MENU:
        switch(mMenuSelection) {
        case PATTERN_NUM:
            mPatternNum += sign;
            if(mPatternNum >= mNumPatterns)
                mPatternNum = mNumPatterns - 1;
            else if(mPatternNum < 0)
                mPatternNum = 0;
            else if(mPlaying)
                StartPattern();
            break;
        case PATTERN_INSTRUMENT:
            mInstrumentNum += sign;
            if(mInstrumentNum >= mNumInstruments)
                mInstrumentNum = mNumInstruments - 1;
            else if(mInstrumentNum < 0)
                mInstrumentNum = 0;
            else if(mPlaying)
                StartPattern();
            break;
        }
        break;
    case WINDOW_PATTERN:
        if(sign == 1 && mPatternData[mPatternNum][mPatternSelection] < b6) {
            mPatternData[mPatternNum][mPatternSelection]++;
        }
        if(sign == -1 && mPatternData[mPatternNum][mPatternSelection] > C1) {
            mPatternData[mPatternNum][mPatternSelection]--;
        }
        break;
    }
}

void
PatternEdit::FetchPatterns(void)
{
    for(int i = 0; i < mNumPatterns; i++) {
        // Get pointer to pattern data
        Sint8* ptr = pattern_list[i];

        mPatternLength[i] = 0;
        // Loop through pattern data and store in list
        int j = 0;
        while(*ptr != END_PATTERN) {
            mPatternData[i][j++] = *ptr++;
            mPatternLength[i]++;
        }
        mPatternData[i][j++] = *ptr;
        mPatternLength[i]++;
    }
}

void
PatternEdit::StorePatterns(void)
{
    for(int i = 0; i < mNumPatterns; i++) {
        // Store pointer to pattern data
        pattern_list[i] = mPatternData[i];
    }
}

void
PatternEdit::StopMode(void)
{
    mPlaying = false;
}

void
PatternEdit::StartMode(void)
{
    Redraw();
}

void
PatternEdit::Debug(void)
{
    printf("%d\n", mActiveWindow);
}

void
PatternEdit::WriteToFile(std::ofstream& fil)
{
    WriteToFile(fil, -1);
}

void
PatternEdit::WriteToFile(std::ofstream& fil,
                         int p)
{
    if(p == -1)
        p = mPatternNum;
    fil << mPatternLength[p] << std::endl;
    for(int i = 0; i < mPatternLength[p]; i++) {
        fil << mPatternData[p][i];
    }
}

void
PatternEdit::ReadFromFile(std::ifstream& fil)
{
    ReadFromFile(fil, -1);
}

void
PatternEdit::ReadFromFile(std::ifstream& fil,
                          int p)
{
    if(fil.good() && !fil.eof() && fil.is_open()) {
        if(p == -1)
            p = mPatternNum;
        fil >> mPatternLength[p];
        for(int i = 0; i < mPatternLength[p]; i++) {
            fil >> mPatternData[p][i];
        }
    }
}
