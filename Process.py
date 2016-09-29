#!/usr/bin/env python
# encoding: utf-8
import json
import os
import argparse
import NameFromIndex
import RollingSplit
import collectAverages

#Constants
CWD = os.getcwd()


#in: 
#   process.py [-h] [-p] /path/to/videos /path/to/OSTs
#   -h      :      help. Ignores all other inputs
#   -p      :      keeps all output folders ( warning: storage intensive. Typically equivalent to 30x audiotrack size, i.e., a 129mb => 3.8gb )

#out:
#   ./[series-name]/episodes/[episode-xx]/timings.txt                     #the final output, a list of timimgs for each song in the given episode
#   ./[series-name]/episodes/[episode-xx]/[episode-xx].[format]           #The raw audio ripped from the given video file via ffmpeg
#   ./[series-name]/episodes/[episode-xx]/cuts/                           #Filled with the 30(or 60?) second cuts of the raw audio via ffmpeg
#   ./[series-name]/episodes/[episode-xx]/prints.json                     #JSON file of all the cuts ran through echoprint-codegen
#   ./[series-name]/tracepaths/                                           #outputs from each step allowing for reconstruction, including things like tracknames
#   ./[series-name]/indexes/                                              #indexes from the OSTs - one per folder/zip file found in the OSTs location


#1. Make dirs
#2. OSTs:
#   a. For each OST directory, create an index with echoprint-codegen -> decode -> inverted index 

def makeFolders():
    seriesName = "Code Geass"
    baseDir = os.path.join(CWD,seriesName)
    epsiodesDir = os.path.join(baseDir, "episodes")
    tracesDir = os.path.join(baseDir, "tracepaths")
    indexDir = os.path.join(baseDir, "indexes")
    os.makedirs(indexDir)
    os.makedirs(tracesDir)
    os.makedirs(epsiodesDir)



def main():
    #arg parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', "--persist", action="store_true",help="Whether to keep all generated files and folder structure after script completes")
    parser.add_argument("videos", type=str, help="Path to the video files")
    parser.add_argument("osts", type=str, help="Path to the OST files")
    args = parser.parse_args()
    

    return 0

if __name__ == "__main__":
    main()