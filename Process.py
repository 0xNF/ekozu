#!/usr/bin/env python
# encoding: utf-8
import json
import os
import argparse
import NameFromIndex
import RollingSplit
import collectAverages


#in: 
#   process.py /path/to/videos /path/to/OSTs
#out:
#   ./[series-name]/episodes/[episode-xx]/timings.txt                     #the final output, a list of timimgs for each song in the given episode
#   ./[series-name]/episodes/[episode-xx]/[episode-xx].[format]           #The raw audio ripped from the given video file via ffmpeg
#   ./[series-name]/episodes/[episode-xx]/cuts/                           #Filled with the 30(or 60?) second cuts of the raw audio via ffmpeg
#   ./[series-name]/episodes/[episode-xx]/prints.json                     #JSON file of all the cuts ran through echoprint-codegen
#   ./[series-name]/tracepaths/                                           #outputs from each step allowing for reconstruction, including things like tracknames
#   ./[series-name]/indexes/                                              #indexes from the OSTs - one per folder/zip file found in the OSTs location
