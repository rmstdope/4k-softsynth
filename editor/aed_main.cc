// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-
#include "AudioEditor.hh"
#undef main

int
main(void)
{
    AudioEditor* aed = new AudioEditor();

    if(aed->Initialize()) {
        printf("Init OK\n");
        aed->MainLoop();
    }

    delete aed;
    return 0;
}
