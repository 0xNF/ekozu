#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import os
import sys
import shutil
import argparse
import subprocess
from MakeTimings import MakeTimings
from RollingSplit import split
from MakePrints import makeWithPath, sortAndWrite
from AIUtils import \
    sortJson, loadJsonFromFile, natural_key
from echoprint_server import \
    load_inverted_index, query_inverted_index, \
    parsed_code_streamer, parsing_code_streamer, \
    create_inverted_index, decode_echoprint

#TODO
#2. make collectAverages...better. Form able to be uploaded to github
#3. make setup.py
#4. Keep log of completed/left-to-do episodes so we can pickup from an arbitrary episode without repeating work.
    #command line option to start at position X

#Constants
CWD = os.getcwd()
Codecs = ['avs', 'cavs', 'aac', 'aac_latm', 'adpcm_vima',\
 'alac', 'ape', 'avc', 'binkaudio_dct', 'binkaudio_rdft',\
 'bmv_audio', 'cook', 'dsicinaudio', 'dvaudio', 'flac',\
 'iac', 'mace3', 'mace6', 'mp1', 'mp2', 'mp3', 'mp3adu',\
 'mp4als', 'opus', 'paf_audio', 'pcm_s24daud', 'ra_144',\
 'ra_288', 'ralf', 'sipr', 'smackaudio', 'tak', 'tta',\
 'vmdaudio', 'westwood_snd1', 'wmalossless', 'wmapro',\
 'wmav1', 'wmav2', 'wmavoice', 'xma1', 'xma2']

#in: 
#   process.py [-h] [-p] /path/to/videos /path/to/OSTs
#   -h      :      help. Ignores all other inputs
#   -p      :      keeps all output folders ( warning: storage intensive. Typically equivalent to 30x audiotrack size, i.e., a 129mb => 3.8gb )

#out:
#   ./[series-name]/episodes/[episode-xx]/timings.txt                     #the final output, a list of timings for each song in the given episode
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
        os.makedirs(p)
        #ffmpeg -i InputVideo.mkv -vn -acodec copy AudioTrack.flac
        ftype = determineAudioFormat(val)
        audiopath = os.path.join(p, "AudioTrack.{0}".format(ftype))
        args = ("ffmpeg", "-loglevel", "quiet", "-i", val, "-vn", "-acodec", "copy", audiopath)
        print("Ripping Audio...{0} of {1}".format(str(idx+1), str(len(fs))))
        subprocess.check_output(args)
        #Splitting into chunks
        print("Splitting Audio")
        splitAudioTrack(audiopath, duration=60, overlap=5)
        #creating prints.json
        print("Producing Prints")
        printsFromSplits(p)
    print("Ripping Audio...Done!".format(str(idx+1), str(len(fs))))
    
def determineAudioFormat(video):
    """Returns the codec (mp3, flac, aac...) of the audio stream using ffmpeg"""
    args = ("ffprobe", "-loglevel", "quiet", "-show_entries", "stream=codec_name", "-i", video)
    output = subprocess.check_output(args)
    streamCodecs = [x.lower().replace('\n','').replace("[stream]","").replace("codec_name=",'') for x in output.split('[/STREAM]') if len(x) > 0]
    streamCodecs = [x for x in streamCodecs if x in Codecs]
    return streamCodecs[0].lower()

def splitAudioTrack(audioFile, duration=60, overlap=5):
    """Splits an audio track into chunks of {duration} seconds each, with {overlap} seconds of overlap. 
    For example, a track with duration=60 and overlap=5 would be split into chunks of 60 seconds, advancing 5 seconds each chunk. 
    The first split track would cover the timespan [0:00 - 1:00] and the second would cover [0:05 - 1:05] and so on"""
    dirname = os.path.join(EPISODESDIR, os.path.dirname(audioFile))
    split(audioFile, duration, overlap, dirname, silent=False)
    os.remove(audioFile)

def printsFromSplits(spath):
    """Produces a prints.json file containing the EchoPrint decodes of each each track contained in the path {spath}"""
    splitsPath = os.path.join(spath, "splits")    
    fname = "prints.json"
    pathA = os.path.join(splitsPath, fname)
    pathB = os.path.join(spath, fname)
    makeWithPath(splitsPath, fname)
    sortAndWrite(pathA)
    shutil.move(pathA, pathB)
    shutil.rmtree(splitsPath)

def makeIndexes(Osts):
    """Creates indexes via the EchoPrint function MakeInvertedIndex and places these indexes under the folder "[series]/indexes/"" """
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
                        #if file is [MP3, FLAC, AAC, WAV, MP4, M4A]   ...    
                        ext = os.path.splitext(file)[1].replace('.','').lower()
                        if ext in Codecs:
                            songs.append(os.path.join(root,file))
            #Echoprint-codegen -s < song_list.txt > song_results.json
            f_name = dir.replace(' ','')+"_song_results.json"            
            makeIndexPrints(songs, os.path.join(path,dir), outName=f_name, outDir=TRACESDIR)

            #purge songs that coudln't be decoded..
            #... TODO ...

            #Sort song_codes by file name
            sortAndWrite(os.path.join(TRACESDIR, f_name))
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
    """Creates the folder structure for the program"""
    shutil.rmtree(BASEDIR, ignore_errors=True)
    os.makedirs(INDEXDIR)
    os.makedirs(TRACESDIR)
    os.makedirs(EPISODESDIR)

def makeIndexPrints(songsList, inDir, outName="prints.json", outDir=os.getcwd()):
    """Makes a prints.json containing the decoded EchoPrints for the index files"""
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


def clean():
    """Removes everything except the song timings for each episode"""
    shutil.rmtree(TRACESDIR)
    shutil.rmtree(INDEXDIR)
    for root,dirs,files in os.walk(EPISODESDIR):
        for name in dirs:
            dir = os.path.join(root,name)
            fs = os.listdir(dir)
            for f in fs:
                if not f.endswith(".txt"):
                    os.remove(os.path.join(dir,f))
#Main
def main():
    OK = True
    #arg parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', "--persist", action="store_true",help="Whether to keep all generated files and folder structure after script completes")
    parser.add_argument('series', help="The name of the series") 
    parser.add_argument("videos", type=str, help="Path to the video files")
    parser.add_argument("osts", type=str, help="Path to the OST files")
    args = parser.parse_args()

    #Error collection for mistyped or invalid input
    Errors = []
    if not os.path.exists(args.videos):
        Errors.append("Error - Videos path \"{0}\" does not exist. Please enter a valid path and try again.".format(args.videos))
        OK = False
    if not os.path.exists(args.osts):
        Errors.append("Error - OST path \"{0}\" does not exist. Please enter a valid path and try again.".format(args.osts))
        OK = False    
    if not OK:
        for error in Errors:
            print(error)
        return 1

    #structure creation
    global BASEDIR, EPISODESDIR, TRACESDIR, INDEXDIR
    BASEDIR = os.path.join(CWD,args.series)
    EPISODESDIR = os.path.join(BASEDIR, "episodes")
    TRACESDIR = os.path.join(BASEDIR, "tracepaths")
    INDEXDIR = os.path.join(BASEDIR, "indexes")
    
    #Real work
    makeFolders(args.series)
    makeIndexes(args.osts)
    ripAudio(args.videos)

    #Producing timings
    MakeTimings(EPISODESDIR, INDEXDIR)

    #Cleanup
    if not args.persist:
        clean()

    return 0

if __name__ == "__main__":
    main()