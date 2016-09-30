#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import json
import os,sys
import shutil
import argparse
import NameFromIndex
import RollingSplit
import collectAverages
from subprocess import Popen, PIPE
import subprocess
from AIUtils import \
    sortJson, loadJsonFromFile, natural_key
from echoprint_server import \
    load_inverted_index, query_inverted_index, \
    parsed_code_streamer, parsing_code_streamer, \
    create_inverted_index, decode_echoprint

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


#1. Make OST indexes (1 per folder in OSTDir)
#2. make episode splits (1 per episode in VideosDir)
#3. make episode prints (1 per split from previous step)
#4. scan for data

def ripAudio(Videos):
    print("Ripping Audio", end='\r')
    fs = []
    for root,dirs,files in os.walk(Videos):
        for file in files:
            fs.append(os.path.join(root, file))
    for idx,val in enumerate(fs):
        p = os.path.join(EPISODESDIR, os.path.basename(val))
        audiopath = os.path.join(p, "AudioTrack.flac")
        os.makedirs(p)
        #ffmpeg -i InputVideo.mkv -vn -acodec copy AudioTrack.flac
        args = ("ffmpeg", "-loglevel", "quiet", "-i", val, "-vn", "-acodec", "copy", audiopath) 
        print("Ripping Audio...{0} of {1}".format(str(idx+1), str(len(fs))), end='\r')
        sys.stdout.flush() 
        subprocess.check_output(args)
    print("Ripping Audio...Done!".format(str(idx+1), str(len(fs))))
    sys.stdout.flush() 
    
def makeSplits(Videos):
    "NYI"
    print ("Ripping audio")
    return 0

def makeEpisodePrints(Videos):
    "NYI"
    "Call out to MakePrints.py"
    return 0

def makeIndexes(Osts):
    print("Creating Indexes")
    for path,dirs,files in os.walk(Osts):
        for dir in dirs:
            print("Preparing " + dir)
            OSTDir = os.path.join(path,dir)
            songlistFile = os.path.join(TRACESDIR, dir.replace(' ', '')+"_song_list.txt")
            indexFile = os.path.join(INDEXDIR, dir.replace(' ', '')+"_index.bin")
            tmpFile = os.path.join(TRACESDIR, dir.replace(' ','')+"_song_results.json")
            songs = []
            for root,dirs,files in os.walk(OSTDir):
                    for file in files:                        
                        songs.append(os.path.join(root,file))
            #Echoprint-codegen -s < song_list.txt > song_results.json
            f_name = dir.replace(' ','')+"_song_results.json"            
            makePrints(songs, os.path.join(path,dir), outName=f_name, outDir=TRACESDIR)

            #purge songs that coudln't be decoded..
            #... NYI ...
            
            #Sort song_codes by file name
            sortByFilename(os.path.join(TRACESDIR, f_name))
            #Load codes
            print("Decoding songs")
            js = loadJsonFromFile(os.path.join(TRACESDIR, f_name))
            withCode_A = [decode_echoprint(str(x["code"]))[1] for x in js if "code" in x]
            codes = []
            for codelist in withCode_A:
                sList = []
                for code in codelist:
                    sList.append(str(code))
                codes.append(",".join(sList))
            print("Creating index at" + indexFile)  
            create_inverted_index(parsed_code_streamer(codes), indexFile)
    print("Finished creating indexes")

#Utility Functions
def makeFolders(series):
    shutil.rmtree(BASEDIR, ignore_errors=True)
    os.makedirs(INDEXDIR)
    os.makedirs(TRACESDIR)
    os.makedirs(EPISODESDIR)

def makePrints(songsList, inDir, outName="prints.json", outDir=os.getcwd()):
    outFile = os.path.join(outDir, outName)
    songlistFile = os.path.join(outDir, os.path.basename(inDir).replace(' ', '')+"_song_list.txt")
    with open(songlistFile, 'w') as f:
       for trackSplit in songsList:
           f.write(trackSplit + "\n")
    args = ("echoprint-codegen", "-s")
    f_out = open(outFile,'w')
    f_in = open(songlistFile, 'r')
    subprocess.call(args, stdin=f_in, stdout=f_out)
    f_out.close()
    f_in.close()

def sortByFilename(file):
    #Sort by filename and push back to disk
    js = sortJson(loadJsonFromFile(file), cmp=natural_key, key=lambda x: x["metadata"]["filename"])
    with open(file, 'w') as f:
        json.dump(js, f)

#Main
def main():
    #arg parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', "--persist", action="store_true",help="Whether to keep all generated files and folder structure after script completes")
    parser.add_argument('series', help="The name of the series")
    parser.add_argument("videos", type=str, help="Path to the video files")
    parser.add_argument("osts", type=str, help="Path to the OST files")
    args = parser.parse_args()

    global BASEDIR, EPISODESDIR, TRACESDIR, INDEXDIR
    BASEDIR = os.path.join(CWD,args.series)
    EPISODESDIR = os.path.join(BASEDIR, "episodes")
    TRACESDIR = os.path.join(BASEDIR, "tracepaths")
    INDEXDIR = os.path.join(BASEDIR, "indexes")
    
    makeFolders(args.series)
    #makeIndexes(args.osts)
    ripAudio(args.videos)
    return 0

if __name__ == "__main__":
    main()