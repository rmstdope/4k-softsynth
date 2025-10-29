#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

Main entry point for 4K Softsynth Editor""""""

This script launches the main application from the src directory.

"""Main entry point for 4K Softsynth EditorMain entry point for 4K Softsynth Editor



import sysThis script launches the main application from the src directory.This script launches the main application from the src directory.

import os

""""""

# Add src directory to path

src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')

if src_dir not in sys.path:

    sys.path.insert(0, src_dir)import sysimport sys



# Import the Editor class from the editor packageimport osimport os

from editor import Editor





def main():# Add src directory to path# Add src directory to path

    """Main entry point"""

    app = Editor()src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')

    return app.run()

if src_dir not in sys.path:if src_dir not in sys.path:



if __name__ == '__main__':    sys.path.insert(0, src_dir)    sys.path.insert(0, src_dir)

    sys.exit(main())


# Import the Editor class from the editor package# Import the Editor class from the editor package

from editor import Editorfrom editor import Editor





def main():def main():

    """Main entry point"""    """Main entry point"""

    app = Editor()    app = Editor()

    return app.run()    return app.run()





if __name__ == '__main__':if __name__ == '__main__':

    sys.exit(main())    sys.exit(main())