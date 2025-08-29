#!/bin/bash


ZIP_LOCATION=$(which zip)

echo $ZIP_LOCATION

$ZIP_LOCATION program.zip backend frontend package.json package-lock.json