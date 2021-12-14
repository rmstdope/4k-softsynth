// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#include <GL/gl.h>

#include <fstream>

#include "glTexFont-r6/glTexFont.h"
#include "EditBase.hh"
#include "Display.hh"
#include "softsynth.h"

const SDLKey EditBase::mNoteKeys[NUM_KEYS] = {
    SDLK_q, SDLK_w, SDLK_e, SDLK_r, SDLK_t, SDLK_y, SDLK_u, SDLK_i, SDLK_o, SDLK_p, 
    SDLK_a, SDLK_s, SDLK_d, SDLK_f, SDLK_g, SDLK_h, SDLK_j, SDLK_k, SDLK_l, 
    SDLK_z, SDLK_x, SDLK_c, SDLK_v, SDLK_b, SDLK_n, SDLK_m, SDLK_COMMA, SDLK_PERIOD
};

EditBase::EditBase() :
    mHelp(false),
    mRedraw(true),
    mPlaying(false),
    mQuit(false),
    mDialogue(NO_DIALOGUE),
    mFilename("")
{
}

void
EditBase::ProcessEvents(SDL_Event* events,
                        int numEvents)
{
#define KEY_TICKS 80
    static SDLKey lastKey = SDLK_SPACE;
    static Uint32 keyStart = 0;
    static bool fastKey = false;
    static bool newKey = false;

    switch(mDialogue) {
    case NO_DIALOGUE:
        for(int i = 0; i < numEvents; i++) {
            switch(events[i].type) {
            case SDL_KEYDOWN:
                fastKey = events[i].key.keysym.mod & (KMOD_LSHIFT|KMOD_RSHIFT);
                switch(events[i].key.keysym.sym) {
                case SDLK_UP:
                    DecSelection();
                    Redraw();
                    break;
                case SDLK_DOWN:
                    IncSelection();
                    Redraw();
                    break;
                case SDLK_RIGHT:
                    Change(1, fastKey);
                    Redraw();
                    break;
                case SDLK_LEFT:
                    Change(-1, fastKey);
                    Redraw();
                    break;
                case SDLK_ESCAPE:
                    mQuit = true;
                    break;
                case SDLK_F10:
                    ToggleHelp();
                    Redraw();
                    break;
                default:
                    KeyPressed(events[i].key.keysym.sym,
                               events[i].key.keysym.mod);
                    Redraw();
                    break;
                }
                lastKey = events[i].key.keysym.sym;
                keyStart = SDL_GetTicks();
                newKey = true;
                break;
            case SDL_KEYUP:
                KeyUnpressed(events[i].key.keysym.sym, events[i].key.keysym.mod);
                lastKey = SDLK_SPACE;
                break;
            case SDL_MOUSEMOTION:
                break;
            }
        }
        // Do hold for arrow keys
        switch(lastKey) {
        case SDLK_RIGHT:
            {
                Uint32 numTicks = SDL_GetTicks() - keyStart;
                while(numTicks > KEY_TICKS) {
                    numTicks -= KEY_TICKS;
                    keyStart += KEY_TICKS;
                    if(!newKey) {
                        Change(1, fastKey);
                    } else {
                        newKey = false;
                    }
                    Redraw();
                }
            }
            break;
        case SDLK_LEFT:
            {
                Uint32 numTicks = SDL_GetTicks() - keyStart;
                while(numTicks > KEY_TICKS) {
                    numTicks -= KEY_TICKS;
                    keyStart += KEY_TICKS;
                    if(!newKey) {
                        Change(-1, fastKey);
                    } else {
                        newKey = false;
                    }
                    Redraw();
                }
            }
            break;
        }
        break;
    case LOAD_DIALOGUE:
    case SAVE_DIALOGUE:
        for(int i = 0; i < numEvents; i++) {
            if(events[i].type == SDL_KEYDOWN) {
                switch(events[i].key.keysym.sym) {
                case SDLK_BACKSPACE:
                    if(mFilename.size()) {
                        mFilename.erase(mFilename.size() - 1);
                    }
                    break;
                case SDLK_ESCAPE:
                    mDialogue = NO_DIALOGUE;
                    break;
                case SDLK_RETURN:
                    if(mFilename.size()) {
                        if(mDialogue == SAVE_DIALOGUE) {
                            PerformSave();
                        } else {
                            PerformLoad();
                        }
                    }
                    break;
                default:
                    if((events[i].key.keysym.sym >= SDLK_a && 
                        events[i].key.keysym.sym <= SDLK_z) || 
                       (events[i].key.keysym.sym >= SDLK_0 && 
                        events[i].key.keysym.sym <= SDLK_9)) {
                        if(mFilename.size() < FILENAME_LENGTH) {
                            char key = 
                                SDL_GetKeyName(events[i].key.keysym.sym)[0];
                            mFilename += key;
                        }
                    }
                }
            }
        }
        break;
    }

    if(mRedraw) {
        mRedraw = false;

        // Clear screen
        Clear();
      
        // Draw
        Draw();
        DrawDialogue();
      
        // Update screen
        Present();
    }
}

void
EditBase::Present(void)
{
    glLoadIdentity();
    SDL_GL_SwapBuffers();
}

void
EditBase::Clear(void)
{
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
}

void
EditBase::Redraw(void)
{
    mRedraw = true;
}

bool
EditBase::ShouldQuit(void) const
{
    return mQuit;
}

bool
EditBase::IsPlaying(void) const
{
    return mPlaying;
}

const char* const
EditBase::GetNote(Sint8 note)
{
    switch(note) {
    case HOLD_1:
        return "HOLD+1";
    case HOLD_2:
        return "HOLD+2";
    case HOLD_3:
        return "HOLD+3";
    case HOLD_4:
        return "HOLD+4";
    case HOLD_5:
        return "HOLD+5";
    case END_PATTERN:
        return "END_PATTERN";
    case ECHO_ON:
        return "ECHO_ON";
    case ECHO_OFF:
        return "ECHO_OFF";
    case STOP:
        return "STOP";
    case c1:
        return "--";
    case C1:
        return "C1";
    case d1:
        return "d1";
    case D1:
        return "D1";
    case e1:
        return "e1";
    case f1:
        return "f1";
    case F1:
        return "F1";
    case g1:
        return "g1";
    case G1:
        return "G1";
    case a1:
        return "a1";
    case A1:
        return "A1";
    case b1:
        return "b1";
    case c2:
        return "c2";
    case C2:
        return "C2";
    case d2:
        return "d2";
    case D2:
        return "D2";
    case e2:
        return "e2";
    case f2:
        return "f2";
    case F2:
        return "F2";
    case g2:
        return "g2";
    case G2:
        return "G2";
    case a2:
        return "a2";
    case A2:
        return "A2";
    case b2:
        return "b2";
    case c3:
        return "c3";
    case C3:
        return "C3";
    case d3:
        return "d3";
    case D3:
        return "D3";
    case e3:
        return "e3";
    case f3:
        return "f3";
    case F3:
        return "F3";
    case g3:
        return "g3";
    case G3:
        return "G3";
    case a3:
        return "a3";
    case A3:
        return "A3";
    case b3:
        return "b3";
    case c4:
        return "c4";
    case C4:
        return "C4";
    case d4:
        return "d4";
    case D4:
        return "D4";
    case e4:
        return "e4";
    case f4:
        return "f4";
    case F4:
        return "F4";
    case g4:
        return "g4";
    case G4:
        return "G4";
    case a4:
        return "a4";
    case A4:
        return "A4";
    case b4:
        return "b4";
    case c5:
        return "c5";
    case C5:
        return "C5";
    case d5:
        return "d5";
    case D5:
        return "D5";
    case e5:
        return "e5";
    case f5:
        return "f5";
    case F5:
        return "F5";
    case g5:
        return "g5";
    case G5:
        return "G5";
    case a5:
        return "a5";
    case A5:
        return "A5";
    case b5:
        return "b5";
    case c6:
        return "c6";
    case C6:
        return "C6";
    case d6:
        return "d6";
    case D6:
        return "D6";
    case e6:
        return "e6";
    case f6:
        return "f6";
    case F6:
        return "F6";
    case g6:
        return "g6";
    case G6:
        return "G6";
    case a6:
        return "a6";
    case A6:
        return "A6";
    case b6:
        return "b6";
    default:
        return "Error!";
    }
}

std::string
EditBase::GetPattern(Sint8 pattern)
{
    std::string str;
    
    if(pattern == LOOP_TRACK)
        str = "Loop";
    else {
        str = '0' + pattern / 100;
        str += '0' + (pattern % 100) / 10;
        str += '0' + pattern % 10;
    }

    return str;
}

WaveForms
EditBase::GetWaveform(WaveformFunc ptr)
{
    if(get_sine_waveform == ptr)
        return SINE;
    if(get_noise_waveform == ptr)
        return NOISE;
    if(get_square_waveform == ptr)
        return SQUARE;
    if(get_sawtooth_waveform == ptr)
        return SAWTOOTH;
    return NUM_WAVEFORMS;
}

WaveformFunc
EditBase::GetWaveformFunc(WaveForms wave)
{
    if(wave == SINE)
        return get_sine_waveform;
    if(wave == NOISE)
        return get_noise_waveform;
    if(wave == SQUARE)
        return get_square_waveform;
    if(wave == SAWTOOTH)
        return get_sawtooth_waveform;
    return 0;
}

void
EditBase::DrawHelp(std::string* strings, 
                   int num)
{
    std::string helpStrings[] = {
        "F1         - Edit Instrument",
        "F2         - Edit Pattern",
        "F3         - Edit Song",
        "F10        - Toggle help",
        "Up/Down    - Change menu option",
        "Right/Left - Change menu value",
        " +LShift   - Change faster",
        "Return     - Select option",
        "Escape     - Exit program",
    };

    glColor3f(0.7f, 0.7f, 0.7f);
    glRectf(Display::SCREEN_WIDTH / 8, Display::SCREEN_HEIGHT / 8, 
            Display::SCREEN_WIDTH - Display::SCREEN_WIDTH / 8, 
            Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 8);
    fontShadow();
    fontShadowColor(0.5, 0.5, 0.5);
    fontColor(0.8, 0.1, 0.1);
    fontSize(10);
    std::string str("Help");
    fontDrawString(Display::SCREEN_WIDTH / 2 - str.size() * 5, 
                   Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 8 - 20, 
                   str.c_str());

    size_t numGen = sizeof(helpStrings) / sizeof(std::string);
    for(int i = 0; i < numGen; i++) {
        fontSize(10);
        fontDrawString(Display::SCREEN_WIDTH / 8 + 10, 
                       Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 8 - 40 - 10 * i, 
                       helpStrings[i].c_str());
    }
    for(int i = 0; i < num; i++) {
        fontSize(10);
        fontDrawString(Display::SCREEN_WIDTH / 8 + 10, 
                       Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 8 - 40 - 10 * (i + numGen), 
                       strings[i].c_str());
    }
}

void
EditBase::ToggleHelp(void)
{ 
    if(mHelp) 
        mHelp = false; 
    else 
        mHelp = true; 
}

void
EditBase::KeyUnpressed(SDLKey key, 
                       SDLMod mod)
{
}

void
EditBase::Save(void)
{
    printf("xxx\n");
    mDialogue = SAVE_DIALOGUE;
}

void
EditBase::Load(void)
{
    mDialogue = LOAD_DIALOGUE;
}

void
EditBase::DrawDialogue(void)
{
    std::string str;

    switch(mDialogue) {
    case NO_DIALOGUE:
        break;
    case LOAD_DIALOGUE:
    case SAVE_DIALOGUE:
        glColor3f(0.7f, 0.7f, 0.7f);
        glRectf(Display::SCREEN_WIDTH / 4, Display::SCREEN_HEIGHT / 4, 
                Display::SCREEN_WIDTH - Display::SCREEN_WIDTH / 4, 
                Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 4);
        if(mDialogue == SAVE_DIALOGUE)
            str = "Save " + GetExtension();
        else
            str = "Load " + GetExtension();
        fontShadow();
        fontShadowColor(0.5, 0.5, 0.5);
        fontColor(0.8, 0.1, 0.1);
        fontSize(10);
        fontDrawString(Display::SCREEN_WIDTH / 2 - str.size() * 5, 
                       Display::SCREEN_HEIGHT - Display::SCREEN_HEIGHT / 4 - 20, 
                       str.c_str());
        fontColor(0.8, 0.1, 0.1);
        fontSize(10);
        str = mFilename;
        while(str.size() < FILENAME_LENGTH)
            str += '_';
        
        fontDrawString(Display::SCREEN_WIDTH / 2 - FILENAME_LENGTH * 5, 
                       Display::SCREEN_HEIGHT / 2, 
                       str.c_str());
        Redraw();
        break;
    }
}

void
EditBase::PerformSave(void)
{
    std::ofstream fil((mFilename + "." + GetExtension()).c_str());
    WriteToFile(fil);
    fil.close();

    mDialogue = NO_DIALOGUE;
}

void
EditBase::PerformLoad(void)
{
    std::ifstream fil((mFilename + "." + GetExtension()).c_str());
    ReadFromFile(fil);
    fil.close();

    mDialogue = NO_DIALOGUE;
}

