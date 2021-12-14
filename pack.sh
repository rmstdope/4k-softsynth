#!/bin/sh

echo '#!/bin/sh
tail -n+3 "$0"|unxz>i;chmod +x i;./i;rm -f i;exit' > $2
xz -c6 --format=lzma $1 >> $2
chmod +x $2
