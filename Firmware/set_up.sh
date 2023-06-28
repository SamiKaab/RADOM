#!/bin/ash
ping -c 1 8.8.8.8 > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "Internet is available. Proceeding with commands..."
  
  # Add your commands here
  # For example:
  echo "Command 1"
  echo "Command 2"
  echo "Command 3"
  
else
  echo "No internet connection found. Please check your internet connection."
fi