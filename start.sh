#!/bin/bash

# Start the bot
echo "Starting CorectBet Bot..."
python bot.py

# If the bot fails, keep the container running for debugging
if [ $? -ne 0 ]; then
    echo "Bot failed to start. Check logs above."
    tail -f /dev/null
fi
