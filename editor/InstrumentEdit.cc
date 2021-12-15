// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#include "InstrumentEdit.hh"
#include "softsynth.h"

#include <glTexFont.h>
#include <string>
#include <GL/gl.h>

InstrumentEdit::InstrumentEdit(int numInstruments) :
    mNumInstruments(10),
    mInstrumentPositionTick(0),
    mInstrumentNum(0),
    mInstrumentSelection(0),
    mAction(0),
    mLastKey(SDLK_ESCAPE),
    mActiveWindow(WINDOW_MENU)
{
    // Setup an instrument
    GetDisplayData();
}

InstrumentEdit::~InstrumentEdit()
{
}

void
InstrumentEdit::AudioCallback(Uint8 *stream, 
                              int len)
{
    Sint16* output = reinterpret_cast<Sint16*>(stream);
    int samples = len / 2;

    int inARow = 0;
    for(int i = 0; i < samples; i++) {
        output[i] = get_instrument_value_c(mInstrumentNum);
         if(output[i] == 0)
             inARow++;
         else
             inARow = 0;
    }
     if(inARow >= 100)
         mPlaying = false;

    mInstrumentPositionTick = SDL_GetTicks();
}

void 
InstrumentEdit::StartInstrument(void)
{
    instrument_hold[mInstrumentNum] = 0x10000000;
    
    mPlaying = true;
}

void 
InstrumentEdit::StopInstrument(void)
{
    mPlaying = false;
}

void
InstrumentEdit::DecSelection(void)
{
    if(mInstrumentSelection > 0)
        mInstrumentSelection--;
}

void
InstrumentEdit::IncSelection(void)
{
    if(mInstrumentSelection < INSTRUMENT_SELECTIONS - 1)
        mInstrumentSelection++;
}

void
InstrumentEdit::KeyPressed(SDLKey key,
                           SDLMod mod)
{
    switch(mActiveWindow) {
    case WINDOW_MENU:
        switch(key) {
        case SDLK_RETURN:
            if(mInstrumentSelection == INSTRUMENT_SAVE) {
                Save();
            } else if(mInstrumentSelection == INSTRUMENT_LOAD) {
                Load();
            }
            break;
        default:
            for(int i = 0; i < NUM_KEYS; i++) {
                int startNote = C3;
                if(mod & KMOD_CAPS)
                    startNote = C1;
                if(key == mNoteKeys[i]) {
                    start_instrument(mInstrumentNum, startNote+i);
                    StartInstrument();
                    mLastKey = key;
                    break;
                }
            }
        }
    case WINDOW_SAVE:
    case WINDOW_LOAD:
        break;
    }
}

void
InstrumentEdit::KeyUnpressed(SDLKey key,
                             SDLMod mod)
{
    if(key == mLastKey) {
        // Get tick
        Uint32 ticks = instrument_ticks[mInstrumentNum];
        ticks -= instrument_definition[mInstrumentNum].attack;
        ticks -= instrument_definition[mInstrumentNum].decay;
        instrument_hold[mInstrumentNum] = ticks;
    }
}

void
InstrumentEdit::Draw(void)
{
    char str[200];
    std::string text;

    // Draw top and bottom lines
    glBegin(GL_LINE_STRIP);
    glColor3f(0.7f, 0.7f, 0.7f);
    glVertex3f(0.0f, Display::SCREEN_HEIGHT - 50, 0.0f);
    glVertex3f(Display::SCREEN_WIDTH, Display::SCREEN_HEIGHT - 50, 0.0f);
    glEnd();
    glBegin(GL_LINE_STRIP);
    glColor3f(0.7f, 0.7f, 0.7f);
    glVertex3f(0.0f, 50, 0.0f);
    glVertex3f(Display::SCREEN_WIDTH, 50, 0.0f);
    glEnd();

    const float height = Display::SCREEN_HEIGHT - 100;
    const float yStart = (Display::SCREEN_HEIGHT - height) / 2;
    const float yEnd = yStart + height;

    // Draw the actual instrument
    glBegin(GL_LINE_STRIP);
    glColor3f(1.0f, 1.0f, 1.0f);
    for(int x = 0; x < Display::SCREEN_WIDTH; x++) {
        float y = Display::SCREEN_HEIGHT / 2;
        y += (mDisplayData[x] / 32767.0f) * (height / 2);
        glVertex3f(GLfloat(x), Display::SCREEN_HEIGHT - y, 0.0f);
    }
    glEnd();

    // Draw volume enveloping
    glBegin(GL_LINE_STRIP);
    glColor3f(0.0f, 1.0f, 0.0f);
    glVertex3f(0.0f, yEnd, 0.0f);
    Uint32 attackTicks = instrument_definition[mInstrumentNum].attack;
    Uint32 decayTicks = instrument_definition[mInstrumentNum].decay;
    Uint32 releaseTicks = instrument_definition[mInstrumentNum].release;
    Uint32 sumTicks = attackTicks + decayTicks + releaseTicks;
    float a = (instrument_definition[mInstrumentNum].attack * Display::SCREEN_WIDTH) / 
        (float)(sumTicks * 2);
    glVertex3f(a, yStart, 0.0f);
    float d = a + (instrument_definition[mInstrumentNum].decay * Display::SCREEN_WIDTH) / 
        (float)(sumTicks * 2);
    float sl = yEnd -
        instrument_definition[mInstrumentNum].sustain * height;
    glVertex3f(d, sl, 0.0f);
    float s = d + Display::SCREEN_WIDTH / 2.0f;
    glVertex3f(s, sl, 0.0f);
    glVertex3f(Display::SCREEN_WIDTH - 1, yEnd, 0.0f);
    glEnd();


    // If we are playing, draw current position
    //   if(mPlayState == PLAY_INSTRUMENT) {
    //     Uint32 tick = SDL_GetTicks() - mInstrumentPositionTick;
    //     int pos = mInstrumentPosition + tick * 44; //44.1
    //     if(pos > mInstrumentLength[mInstrumentNum]) {
    //       if(mInstrumentLoop) {
    // 	pos %= mInstrumentLength[mInstrumentNum];
    //       } else {
    // 	pos = mInstrumentLength[mInstrumentNum] - 1;
    //       }
    //     }
    //     int linePos = pos * SCREEN_WIDTH / mInstrumentLength[mInstrumentNum];
    //     glBegin(GL_LINES);
    //     glColor3f(1.0f, 0.0f, 0.0f);
    //     glVertex3f(linePos, 0.0f, 0.0f);
    //     glVertex3f(linePos, SCREEN_HEIGHT, 0.0f);
    //     glEnd();
    //   } 

//     fontShadow();
//     fontShadowColor(0.5, 0.5, 0.5);
//     fontColor(1,0,0);

    for(int i = 0; i < INSTRUMENT_SELECTIONS; i++) {
        switch(i) {
        case INSTRUMENT_NUM:
            snprintf(str, 200, "Instrument: %d", mInstrumentNum);
            break;
        case INSTRUMENT_WAVEFORM:
            switch(GetWaveform(instrument_definition[mInstrumentNum].waveForm)) {
            case SINE:
                snprintf(str, 200, "Waveform: Sine");
                break;
            case NOISE:
                snprintf(str, 200, "Waveform: Noise");
                break;
            case SQUARE:
                snprintf(str, 200, "Waveform: Square");
                break;
            case SAWTOOTH:
                snprintf(str, 200, "Waveform: Sawtooth");
                break;
            }
            break;
        case INSTRUMENT_ATTACK:
            snprintf(str, 200, "Attack: %d", instrument_definition[mInstrumentNum].attack);
            break;
        case INSTRUMENT_DECAY:
            snprintf(str, 200, "Decay: %d", instrument_definition[mInstrumentNum].decay);
            break;
        case INSTRUMENT_SUSTAIN:
            snprintf(str, 200, "Sustain: %.2f", instrument_definition[mInstrumentNum].sustain);
            break;
        case INSTRUMENT_RELEASE:
            snprintf(str, 200, "Release: %d", instrument_definition[mInstrumentNum].release);
            break;
        case INSTRUMENT_SWEEP:
            snprintf(str, 200, "Sweep: %.8f", instrument_definition[mInstrumentNum].sweep);
            break;
        case INSTRUMENT_MODULATION:
            snprintf(str, 200, "Modulation: %.6f", instrument_definition[mInstrumentNum].modulation);
            break;
        case INSTRUMENT_DELIMITER_1:
            snprintf(str, 200, "  ---  ");
            break;
        case INSTRUMENT_SAVE:
            snprintf(str, 200, "Save Instrument");
            break;
        case INSTRUMENT_LOAD:
            snprintf(str, 200, "Load Instrument");
            break;
        }
        
        // Draw Text
        fontSize(10);
        if(mInstrumentSelection == i) {
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
            "a-z[+Shift]- Play note",
        };

        DrawHelp(helpStrings, sizeof(helpStrings) / sizeof(std::string));
    }
}

void
InstrumentEdit::Change(int sign,
                       bool moveFast)
{
    int wave;

    switch(mInstrumentSelection) {
    case INSTRUMENT_NUM:
        StopInstrument();
        mInstrumentNum += sign;
        if(mInstrumentNum >= mNumInstruments)
            mInstrumentNum = mNumInstruments - 1;
        if(mInstrumentNum < 0)
            mInstrumentNum = 0;
        break;
    case INSTRUMENT_WAVEFORM:
        wave = GetWaveform(instrument_definition[mInstrumentNum].waveForm);
        wave += sign;
        if(wave == NUM_WAVEFORMS)
            wave = NUM_WAVEFORMS;
        if(wave < 0)
            wave = 0;
        switch(wave) {
        case SINE:
            instrument_definition[mInstrumentNum].waveForm = get_sine_waveform;
            break;
        case NOISE:
            instrument_definition[mInstrumentNum].waveForm = get_noise_waveform;
            break;
        case SQUARE:
            instrument_definition[mInstrumentNum].waveForm = get_square_waveform;
            break;
        case SAWTOOTH:
            instrument_definition[mInstrumentNum].waveForm = get_sawtooth_waveform;
            break;
        }
        break;
    case INSTRUMENT_ATTACK:
        if(moveFast)
            instrument_definition[mInstrumentNum].attack += sign * 50;
        else
            instrument_definition[mInstrumentNum].attack += sign;
        if(instrument_definition[mInstrumentNum].attack < 0)
            instrument_definition[mInstrumentNum].attack = 0;
        break;
    case INSTRUMENT_DECAY:
        if(moveFast)
            instrument_definition[mInstrumentNum].decay += sign * 50;
        else
            instrument_definition[mInstrumentNum].decay += sign;
        if(instrument_definition[mInstrumentNum].decay < 0)
            instrument_definition[mInstrumentNum].decay = 0;
        break;
    case INSTRUMENT_SUSTAIN:
        if(moveFast)
            instrument_definition[mInstrumentNum].sustain += sign * 0.1f;
        else
            instrument_definition[mInstrumentNum].sustain += sign * 0.01f;
        if(instrument_definition[mInstrumentNum].sustain < 0.0f)
            instrument_definition[mInstrumentNum].sustain = 0.0f;
        if(instrument_definition[mInstrumentNum].sustain > 1.0f)
            instrument_definition[mInstrumentNum].sustain = 1.0f;
        break;
    case INSTRUMENT_RELEASE:
        if(moveFast)
            instrument_definition[mInstrumentNum].release += sign * 50;
        else
            instrument_definition[mInstrumentNum].release += sign;
        if(instrument_definition[mInstrumentNum].release < 0)
            instrument_definition[mInstrumentNum].release = 0;
        break;
    case INSTRUMENT_SWEEP:
        if(moveFast)
            instrument_definition[mInstrumentNum].sweep += sign * 0.0000001f;
        else
            instrument_definition[mInstrumentNum].sweep += sign * 0.00000001f;
        break;
    case INSTRUMENT_MODULATION:
        if(moveFast)
            instrument_definition[mInstrumentNum].modulation += sign * 0.0001f;
        else
            instrument_definition[mInstrumentNum].modulation += sign * 0.00001f;
        break;
//     case INSTRUMENT_ACTION:
//         mAction += sign;
//         if(mAction == NUM_ACTIONS)
//             mAction = NUM_ACTIONS - 1;
//         if(mAction < 0)
//             mAction = 0;
//         break;
    }
    GetDisplayData();
}

void
InstrumentEdit::StopMode(void)
{
    mPlaying = false;
}

void
InstrumentEdit::StartMode(void)
{
    Redraw();
}

void
InstrumentEdit::GetDisplayData(void)
{
    start_instrument(mInstrumentNum, a3);

    // Set fake length
    instrument_hold[mInstrumentNum] = 
        instrument_definition[mInstrumentNum].attack +
        instrument_definition[mInstrumentNum].decay +
        instrument_definition[mInstrumentNum].release;
    
    int instrumentLength = instrument_hold[mInstrumentNum] * 2;

    int oldInstrumentPos = 0;
    for(int x = 0; x < Display::SCREEN_WIDTH; x++) {
        int instrumentPos = (instrumentLength * x) / Display::SCREEN_WIDTH;
        mDisplayData[x] = get_instrument_value_c(mInstrumentNum);
        for(int i = 0; i < instrumentPos - oldInstrumentPos; i++)
             get_instrument_value_c(mInstrumentNum);
        oldInstrumentPos = instrumentPos;
    }
}

void
InstrumentEdit::WriteToFile(std::ofstream& fil)
{
    fil << GetWaveform(instrument_definition[mInstrumentNum].waveForm) << std::endl;
    fil << instrument_definition[mInstrumentNum].attack << std::endl;
    fil << instrument_definition[mInstrumentNum].decay << std::endl;
    fil << instrument_definition[mInstrumentNum].sustain << std::endl;
    fil << instrument_definition[mInstrumentNum].release << std::endl;
    fil << instrument_definition[mInstrumentNum].modulation << std::endl;
    fil << instrument_definition[mInstrumentNum].sweep << std::endl;
}

void
InstrumentEdit::ReadFromFile(std::ifstream& fil)
{
    if(fil.good() && !fil.eof() && fil.is_open()) {
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
    GetDisplayData();
}
