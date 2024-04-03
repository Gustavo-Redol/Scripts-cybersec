#!/bin/bash

echo "Metanalyzer: Automated metadata analyzer"
echo "Created by Gustavo Redol"
echo "Usage: metanalyzer -> answer the questions"

# Define the search mechanism via terminal
SEARCH="lynx"

# Define the target and file type to be searched
read -p "Enter the URL of the target: " TGT
read -p "Enter the file type, e.g. PDF DOC DOCX... ONLY ONE AT A TIME: " TYPE
echo "Starting search"

# Searches with Google dorks in the target for files in the specified format and returns the clean result
$SEARCH --dump "https://google.com/search?&q=site:$TGT+ext:$TYPE" | grep ".$TYPE" | cut -d "=" -f2 | egrep -v "site|google" | sed 's/...$//' > /tmp/found

# Downloads the files and analyzes the metadata"
echo "Found files: "

echo "Downloading found files, this may take a while..."
mkdir archives
cd archives
for url in $(cat /tmp/found); do
    wget -q $url 
    exiftool *.$TYPE
done

# Removes the temporary file if indicated
cd ..
rm -rf archives

echo "Search completed"
