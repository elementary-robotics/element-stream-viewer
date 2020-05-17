#!/bin/bash

# Launch the VNC
if [ ${GRAPHICS} ]; then
    /usr/bin/supervisord -c /etc/supervisor/supervisord.conf &
    sleep 5
fi

python3 run.py
