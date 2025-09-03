#!/bin/bash

INCLUDED_FILES="backend frontend package.json package-lock.json LICENSE"

FILE="program.zip"

if [ -e $FILE ]; then
    rm $FILE
    echo "Removed old build file."
fi

ZIP_LOCATION=$(which zip)

$ZIP_LOCATION -r $FILE $INCLUDED_FILES -x *.pyc __pycache__/*