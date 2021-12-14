// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#include <glTexFont.h>
#include <string>
#include <iostream>

#include "TrackEdit.hh"
#include "PatternEdit.hh"
#include "Display.hh"
#include "softsynth.h"

TrackEdit::TrackEdit(PatternEdit* pEdit,
                     int numInstruments,
                     int numPatterns) :
    mNumInstruments(numInstruments),
    mNumPatterns(numPatterns),
    mMenuSelection(0),
    mTrackSelection(0),
    mTrackNum(0),
    mLastMute(true),
    mActiveWindow(WINDOW_MENU),
    mPatternEdit(pEdit)
{
    mMutedTrack[0] = 0;
    mMutedTrack[1] = LOOP_TRACK;

    // Get tracks
    FetchTracks();
    
    for(int i = 0; i < mNumInstruments; i++) {
        Mute(i, false);
    }
}

TrackEdit::~TrackEdit()
{
}

void
TrackEdit::AudioCallback(Uint8 *stream, 
                           int len)
{
    softsynth_play(0, stream, len);
}

void 
TrackEdit::StartSong(void)
{
    // Calculate correct indices
    int ticks = 0;
    for(int i = 0; i < mNumInstruments; i++) {
        track_index[i] = -1;
    }
    if(mTrackSelection != 0) {
        while(track_index[mTrackNum] == -1 ||
              track_index[mTrackNum] != mTrackSelection - 1 ||
              pattern_list[track_list[mTrackNum][track_index[mTrackNum]]][pattern_index[mTrackNum] + 1] != END_PATTERN) {
//         while(track_index[mTrackNum] != mTrackSelection) {
            
            for(int i = 0; i < mNumInstruments; i++) {
                if(track_index[i] == -1) {
                    track_index[i] = 0;
                    pattern_index[i] = 0;
                } else {
                    pattern_index[i]++;
                }
                int p = track_list[i][track_index[i]];
                while(pattern_list[p][pattern_index[i]] == ECHO_ON ||
                      pattern_list[p][pattern_index[i]] == ECHO_OFF) {
                    pattern_index[i]++;
                }
                if(pattern_list[p][pattern_index[i]] == END_PATTERN) {
                    track_index[i]++;
                    pattern_index[i] = 0;
                }
                p = track_list[i][track_index[i]];
                if(p == LOOP_TRACK) {
                    track_index[i] = 0;
                    pattern_index[i] = 0;
                }
                p = track_list[i][track_index[i]];
//                 if(i == 3 || i == 0)
//                     printf("instrument=%d:track:{index=%d}:pattern="
//                            "{num=%d,index=%d:data=%d}\n",
//                            i, track_index[i], p, pattern_index[i],
//                            pattern_list[p][pattern_index[i]]);
            }
            ticks += ROW_TICKS;
        }
    }

//     for(int i = 0; i < mNumInstruments; i++) {
//         int p = track_list[i][track_index[i]];
//         printf("instrument=%d:track:{index=%d}:pattern="
//                "{num=%d,index=%d:data=%d}\n",
//                i, track_index[i], p, pattern_index[i],
//                pattern_list[p][pattern_index[i]]);
//     }
        
    mPlaying = true;
}

void 
TrackEdit::StopSong(void)
{
    mPlaying = false;
}

void
TrackEdit::DecSelection(void)
{
    switch(mActiveWindow) {
    case WINDOW_MENU:
        if(mMenuSelection > 0)
            mMenuSelection--;
        if(mMenuSelection < mNumInstruments)
            mTrackNum = mMenuSelection;
        break;
    case WINDOW_TRACK:
        if(mTrackSelection > 0)
            mTrackSelection--;
        break;
    }
}

void
TrackEdit::IncSelection(void)
{
    switch(mActiveWindow) {
    case WINDOW_MENU:
        if(mMenuSelection < TRACK_SELECTIONS - 1 + mNumInstruments)
            mMenuSelection++;
        if(mMenuSelection < mNumInstruments)
            mTrackNum = mMenuSelection;
        break;
    case WINDOW_TRACK:
        if(mTrackSelection < mTrackLength[mTrackNum] - 2)
            mTrackSelection++;
        break;
    }
}

void
TrackEdit::KeyPressed(SDLKey key,
                      SDLMod mod)
{
    switch(key) {
    case SDLK_RETURN:
        if(mMenuSelection == TRACK_SAVE + mNumInstruments) {
            Save();
        } else if(mMenuSelection == TRACK_LOAD + mNumInstruments) {
            Load();
        }
        break;
    case SDLK_F11:
        for(int i = 0; i < mNumInstruments; i++)
            Mute(i, mLastMute);
        if(mLastMute)
            mLastMute = false;
        else
            mLastMute = true;
        break;
    case SDLK_PAGEDOWN:
        if(mActiveWindow == WINDOW_TRACK) {
            if(mTrackNum < mNumInstruments - 1) {
                mTrackNum++;
                mMenuSelection = mTrackNum;
            }
        }
        break;
    case SDLK_PAGEUP:
        if(mActiveWindow == WINDOW_TRACK) {
            if(mTrackNum > 0) {
                mTrackNum--;
                mMenuSelection = mTrackNum;
            }
        }
        break;
    case SDLK_TAB:
        if(mActiveWindow == WINDOW_MENU) {
            mActiveWindow = WINDOW_TRACK;
            if(mTrackSelection >= mTrackLength[mTrackNum] - 1)
                mTrackSelection = mTrackLength[mTrackNum] - 2;
        } else {
            mActiveWindow = WINDOW_MENU;
        }
        break;
    case SDLK_SPACE:
        if(mPlaying)
            StopSong();
        else
            StartSong();
        break;
    }

    if(mActiveWindow == WINDOW_TRACK) {
        switch(key) {
        case SDLK_BACKSPACE:
            mTrackData[mTrackNum][mTrackSelection] = 0;
            IncSelection();
            break;
        case SDLK_INSERT:
            if(mTrackLength[mTrackNum] <= MAX_TRACK_LENGTH) {
                int len = mTrackLength[mTrackNum] - mTrackSelection;
                mTrackLength[mTrackNum]++;
                for(int i = 0; i < len; i++) {
                    mTrackData[mTrackNum][mTrackSelection - i + len] =
                        mTrackData[mTrackNum][mTrackSelection - i - 1 + len];
                }
                mTrackData[mTrackNum][mTrackSelection] = 0;
            }
            break;
        case SDLK_DELETE:
            if(mTrackLength[mTrackNum] > 2) {
                int len = mTrackLength[mTrackNum] - mTrackSelection - 1;
                for(int i = 0; i < len; i++) {
                    mTrackData[mTrackNum][mTrackSelection + i] = 
                        mTrackData[mTrackNum][mTrackSelection + 1 + i];
                }
                mTrackLength[mTrackNum]--;
                if(mTrackSelection >= mTrackLength[mTrackNum] - 1)
                    mTrackSelection = mTrackLength[mTrackNum] - 2;
            }
            break;
        case SDLK_KP_PLUS:
        case SDLK_PLUS:
            if(mTrackLength[mTrackNum] <= MAX_TRACK_LENGTH) {
                mTrackData[mTrackNum][mTrackLength[mTrackNum] - 1] = 0;
                mTrackLength[mTrackNum]++;
                mTrackData[mTrackNum][mTrackLength[mTrackNum] - 1] = 
                    LOOP_TRACK;
            }
            break;
        case SDLK_KP_MINUS:
        case SDLK_MINUS:
            if(mTrackLength[mTrackNum] > 2) {
                mTrackLength[mTrackNum]--;
                mTrackData[mTrackNum][mTrackLength[mTrackNum] - 1] = 
                    LOOP_TRACK;
            }
            break;
         default:
             if(key >= SDLK_0 && key <= SDLK_9) {
                 if(key - SDLK_0 < mNumPatterns) {
                     if(mTrackData[mTrackNum][mTrackSelection] * 10 + 
                        key - SDLK_0 <= 127)
                         mTrackData[mTrackNum][mTrackSelection] *= 10;
                     else
                         mTrackData[mTrackNum][mTrackSelection] = 0;
                     mTrackData[mTrackNum][mTrackSelection] += key - SDLK_0;
                     if(mTrackData[mTrackNum][mTrackSelection] >= mNumPatterns)
                         mTrackData[mTrackNum][mTrackSelection] = key - SDLK_0;
                 }
             }
        }
    }
}

void
TrackEdit::Draw(void)
{
    char str[200];
    std::string text;

    // Draw track info
    for(int j = 0; j < 5; j++) {
        int track = mTrackNum - 2 + j;
        if(track < 0 || track >= mNumInstruments)
            continue;
        int xStart = Display::SCREEN_WIDTH / 2 + (j - 2) * 80 + 40;
        float color = 1.0f - 0.3 * abs(j - 2);
        fontSize(10);
        if(IsMuted(track)) {
            fontColor(0.3f, 0.1f, 0.1f);
        } else {
            fontColor(color, color, color);
        }
        sprintf(str, "Track %d", track);
        fontDrawString(xStart, 
                       Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 4, 
                       str);
        for(size_t i = 0; i < mTrackLength[track]; i++) {
            fontSize(10);
            if(IsMuted(track)) {
                fontColor(0.3f, 0.1f, 0.1f);
            } else {
                fontColor(color, color, color);
            }
            if(mActiveWindow == WINDOW_TRACK &&
               mTrackSelection == i && track == mTrackNum)
                fontColor(1, 0, 0);
            text = GetPattern(mTrackData[track][i]);
            if(mPlaying && track_index[track] == i) {
                text = "->" + text;
            }
            fontDrawString(xStart, 
                           Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 4 - 10 * (i + 1), 
                           text.c_str());
        }
    }
    
    // Draw track menu
    for(int i = 0; i < TRACK_SELECTIONS + mNumInstruments; i++) {
        if(i == TRACK_DELIMITER_1 + mNumInstruments) {
            sprintf(str, "  ---  ");
        } else if(i == TRACK_SAVE + mNumInstruments) {
            sprintf(str, "Save Track");
        } else if(i == TRACK_LOAD + mNumInstruments) {
            sprintf(str, "Load Track");
        } else {
            if(IsMuted(i - TRACK_DELIMITER_1))
                sprintf(str, "Instrument %d: Muted", i - TRACK_DELIMITER_1);
            else
                sprintf(str, "Instrument %d: On", i - TRACK_DELIMITER_1);
        }
        
        // Draw Text
        fontSize(10);
        if(mMenuSelection == i) {
            fontColor(1, 0, 0);
            text = std::string("-> ") + str;
        } else {
            fontColor(0.8f, 0.8f, 0.8f);
            text = str;
        }
        fontDrawString (0, Display::SCREEN_HEIGHT - 10 * (i + 1), 
                        text.c_str());
    }

    // Draw help?
    if(mHelp) {
        std::string helpStrings[] = {
            "Space      - Play/Stop pattern",
            "Tab        - Toggle menu/edit",
            "F11        - Mute/unmute all",
            "+          - Increase pattern length",
            "-          - Decrease pattern length",
            "Del        - Remove beat at current pos",
            "Ins        - Insert beat at current pos",
            "Right/Left - Inc/Dec note value",
            "PgUp/Pgdn  - Select next/prev instrument",
            "0-9        - Set pattern",
        };

        DrawHelp(helpStrings, sizeof(helpStrings) / sizeof(std::string));
    }

    if(mPlaying)
        Redraw();
}

void
TrackEdit::Change(int sign,
                  bool moveFast)
{
    switch(mActiveWindow) {
    case WINDOW_MENU:
        if(mMenuSelection < TRACK_DELIMITER_1 + mNumInstruments) {
            Mute(mMenuSelection - TRACK_DELIMITER_1,
                 !IsMuted(mMenuSelection - TRACK_DELIMITER_1));
        }
        break;
    case WINDOW_TRACK:
        if(sign == 1 && mMenuSelection < mNumInstruments - 1) {
            mMenuSelection++;
            mTrackNum = mMenuSelection;
            if(mTrackSelection >= mTrackLength[mTrackNum] - 1)
                mTrackSelection = mTrackLength[mTrackNum] - 2;
        }
        if(sign == -1 && mMenuSelection != 0) {
            mMenuSelection--;
            mTrackNum = mMenuSelection;
            if(mTrackSelection >= mTrackLength[mTrackNum] - 1)
                mTrackSelection = mTrackLength[mTrackNum] - 2;
        }
        break;
    }
}

void
TrackEdit::FetchTracks(void)
{
    for(int i = 0; i < mNumInstruments; i++) {
        // Get pointer to pattern data
        Sint8* ptr = track_list[i];

        mTrackLength[i] = 0;
        // Loop through pattern data and store in list
        int j = 0;
        while(*ptr != LOOP_TRACK) {
            mTrackData[i][j++] = *ptr++;
            mTrackLength[i]++;
        }
        mTrackData[i][j++] = *ptr;
        mTrackLength[i]++;
    }
}

void
TrackEdit::StoreTracks(void)
{
    for(int i = 0; i < mNumInstruments; i++) {
        // Store pointer to track data
        if(IsMuted(i)) {
            track_list[i] = mMutedTrack;
        } else {
            track_list[i] = mTrackData[i];
        }
    }
}

void
TrackEdit::StopMode(void)
{
    mPlaying = false;
}

void
TrackEdit::StartMode(void)
{
    StoreTracks();
    Redraw();
}

void
TrackEdit::WriteToFile(std::ofstream& fil)
{
    // Save num instruments
    fil << mNumInstruments << std::endl;
    // Save num patterns
    fil << mNumPatterns << std::endl;
    
    // Save instruments
    for(int i = 0; i < mNumInstruments; i++) {
        fil << GetWaveform(instrument_definition[i].waveForm) << std::endl;
        fil << instrument_definition[i].attack << std::endl;
        fil << instrument_definition[i].decay << std::endl;
        fil << instrument_definition[i].sustain << std::endl;
        fil << instrument_definition[i].release << std::endl;
        fil << instrument_definition[i].modulation << std::endl;
        fil << instrument_definition[i].sweep << std::endl;
    }
 
    // Save patterns
    for(int i = 0; i < mNumPatterns; i++) {
        mPatternEdit->WriteToFile(fil, i);
    }
    
    // Save tracks
    for(int i = 0; i < mNumInstruments; i++) {
        fil << mTrackLength[i] << std::endl;
        for(int j = 0; j < mTrackLength[i]; j++) {
            fil << mTrackData[i][j];
        }
    }
}

void
TrackEdit::ReadFromFile(std::ifstream& fil)
{
    if(fil.good() && !fil.eof() && fil.is_open()) {
        // Load num instruments
        int numInstruments;
        fil >> numInstruments;
        if(numInstruments != mNumInstruments) {
            std::cout << "# instruments in fil (" << numInstruments
                      << ") does not match # instruments in AED ("
                      << mNumInstruments << ").";
            return;
        }

        // Load num patterns
        int numPatterns;
        fil >> numPatterns;
        if(numPatterns != mNumPatterns) {
            std::cout << "# patterns in fil (" << numPatterns
                      << ") does not match # patterns in AED ("
                      << mNumPatterns << ").";
            return;
        }

        // Load instruments
        for(int i = 0; i < mNumInstruments; i++) {
            int waveform;
            fil >> waveform;
            instrument_definition[mInstrumentNum].waveForm = 
                GetWaveformFunc(static_cast<WaveForms>(waveform));
            fil >> instrument_definition[mInstrumentNum].attack;
            fil >> instrument_definition[mInstrumentNum].decay;
            fil >> instrument_definition[mInstrumentNum].sustain;
            fil >> instrument_definition[mInstrumentNum].release;
            fil >> instrument_definition[mInstrumentNum].modulation;
            fil >> instrument_definition[mInstrumentNum].sweep;
        }

        // Load patterns
        for(int i = 0; i < mNumPatterns; i++) {
            mPatternEdit->ReadFromFile(fil, i);
        }
 
        // Save tracks
        for(int i = 0; i < mNumInstruments; i++) {
            fil >> mTrackLength[i];
            for(int j = 0; j < mTrackLength[i]; j++) {
                fil >> mTrackData[i][j];
            }
        }
    }
}

void
TrackEdit::Mute(int instrument,
                bool mute)
{
    mInstrumentMuted[instrument] = mute;
    if(mute) {
        track_list[instrument] = mMutedTrack;
        track_index[instrument] = -1;
    } else {
        track_list[instrument] = mTrackData[instrument];

        // Calculate correct indices
        int numTicks = ticks;
        track_index[instrument] = -1;
        while(numTicks > ROW_TICKS) {
            if(track_index[instrument] == -1) {
                track_index[instrument] = 0;
                pattern_index[instrument] = 0;
//                 printf("Clearing for start\n");
            } else {
                pattern_index[instrument]++;
//                 printf("Increasing pattern_index to %d\n",
//                        pattern_index[instrument]);
            }
            int p = track_list[instrument][track_index[instrument]];
            while(pattern_list[p][pattern_index[instrument]] == ECHO_ON ||
               pattern_list[p][pattern_index[instrument]] == ECHO_OFF) {
                pattern_index[instrument]++;
            }
//             printf("track:{index=%d}:pattern={num=%d,index=%d:data=%d}\n",
//                    track_index[instrument], p, pattern_index[instrument],
//                    pattern_list[p][pattern_index[instrument]]);
//             printf("Pattern data is %d\n",
//                    pattern_list[p][pattern_index[instrument]]);
            if(pattern_list[p][pattern_index[instrument]] == END_PATTERN) {
                track_index[instrument]++;
                pattern_index[instrument] = -1;
//                 printf("Increasing track_index to %d\n",
//                        track_index[instrument]);
            }
            p = track_list[instrument][track_index[instrument]];
            if(p == LOOP_TRACK) {
                track_index[instrument] = 0;
                pattern_index[instrument] = 0;
//                 printf("Clearing for loop\n");
            }
            numTicks -= ROW_TICKS;
//             printf("One tick processed\n");
        }
    }
}
  
bool
TrackEdit::IsMuted(int instrument) const
{
    return mInstrumentMuted[instrument];
}

// void
// TrackEdit::CalculatePositions(void)
// {
//     Sint8* trackPtr;
//     for(int i = 0; i < mNumInstruments; i++) {
//         int numTicks = ticks;
//         ptr = track_list[i];
//         ptr += track_index[i];

        
//         while(numTicks > ROW_TICKS) {
            
//         ROW_TICKS
//     }
// }
  
