#!/usr/bin/env python
# encoding: utf-8
import os
import subprocess
import argparse
import re
import json
from AIUtils import natural_key, natural_sort, sortJson

#Constants
FILEPATTERN = "cut_([0-9]+)_([0-9]+)\.(.*)"
CWD = os.getcwd()
JSONFILE = os.path.join(CWD, "prints.json")

#Primary functions
def makePrints(inDir):
    audioTracks = listAudioFiles(inDir)
    splitsListFile = os.path.join(CWD, "splits_list.txt")
    with open(splitsListFile, 'w') as f:
       for trackSplit in audioTracks:
           f.write(trackSplit + "\n")
    args = ("echoprint-codegen", "-s")
    f_out = open(JSONFILE,'w')
    f_in = open(splitsListFile, 'r')
    subprocess.call(args, stdin=f_in, stdout=f_out)
    f_out.close()
    f_in.close()

def listAudioFiles(inDir):
    fulls = []
    matcher = re.compile(FILEPATTERN)
    for path,dirs,files in os.walk(inDir):
        for f in files:
            if(matcher.match(f)):
                fulls.append(os.path.join(path,f))
    return natural_sort(fulls)

#Main
def main():
    #arg parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('indir', type=str, help="Directory containing split audio files")
    args = parser.parse_args()
    abspath = os.path.abspath(args.indir)
    #Make prints
    makePrints(abspath)
    #Sort by filename and push back to disk
    with open(JSONFILE, 'r') as f:
        jstring = "".join(f.readlines())
        js = json.loads(jstring)
    js = sortJson(js, cmp=natural_key, key=lambda x: x["metadata"]["filename"])
    with open(JSONFILE, 'w') as f:
        json.dump(js, f)

if __name__ == "__main__":
    main()