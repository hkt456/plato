#!/bin/bash

# Start Google Chrome with remote debugging enabled
google-chrome --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir="$HOME/.config/google-chrome"
