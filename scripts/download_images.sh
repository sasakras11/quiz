#!/bin/bash

# Create images directory if it doesn't exist
mkdir -p app/public/images

# Download images
curl https://i.imgur.com/eovHormozi.jpg -o app/public/images/hormozi.jpg
curl https://i.imgur.com/mrbeast.jpg -o app/public/images/mrbeast.jpg
curl https://i.imgur.com/garyvee.jpg -o app/public/images/garyvee.jpg

echo "Images downloaded successfully!" 