#!/usr/bin/env python
# encoding: utf-8
import os
import subprocess
import argparse
import re
import json
from AIUtils import natural_key,\
                    natural_sort,\
                    sortJson,\
                    loadJsonFromFile

#Constants
FILEPATTERN = "cut_([0-9]+)_([0-9]+)\.(.*)"
CWD = os.getcwd()

#Primary functions
def makePrints(songsList, inDir, outName="prints.json", outDir=os.getcwd()):
    outFile = os.path.join(inDir, outName)
    songlistFile = os.path.join(inDir, "splits_list.txt")
    with open(songlistFile, 'w') as f:
       for trackSplit in songsList:
           f.write(trackSplit + "\n")
    args = ("echoprint-codegen", "-s")
    f_out = open(outFile,'w')
    f_in = open(songlistFile, 'r')
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

def sortAndWrite(file):
    """Sort a prints.json by filename and push back to disk"""
    js = sortJson(loadJsonFromFile(file), cmp=natural_key, key=lambda x: x["metadata"]["filename"])
    with open(file, 'w') as f:
        json.dump(js, f)

def makeWithPath(path, fname):
    abspath = os.path.abspath(path)
    files = listAudioFiles(abspath)
    makePrints(files, abspath, outName=fname)    

#Main
def main():
    #arg parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('indir', type=str, help="Directory containing split audio files")
    args = parser.parse_args()
    abspath = os.path.abspath(args.indir)
    #Make prints
    JSONFILE = os.path.join(abspath,"prints.json")
    makePrints(listAudioFiles(abspath), abspath, os.path.basename(JSONFILE))
    #Sort by filename and push back to disk
    sortAndWrite(JSONFILE)
    

if __name__ == "__main__":
    main()