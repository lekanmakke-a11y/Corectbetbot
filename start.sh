#!/bin/bash

# Start health check in background
python health.py &

# Start the bot
echo "Starting CorectBet Bot..."
python bot.py

# If the bot crashes, restart it
while [ $? -ne 0 ]; do
    echo "Bot crashed! Restarting in 5 seconds..."
    sleep 5
    python bot.py
done
