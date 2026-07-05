#!/bin/bash

sudo rfcomm release /dev/rfcomm0 2>/dev/null

bluetoothctl <<EOF
connect 12:34:5A:05:9C:54
quit
EOF

sudo rfcomm bind /dev/rfcomm0 12:34:5A:05:9C:54 1
