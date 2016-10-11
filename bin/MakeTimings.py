#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import json
import datetime
import os,sys
import shutil
import argparse
import subprocess
import NameFromIndex
import collectAverages
from RollingSplit import split
from MakePrints import makeWithPath, sortAndWrite
from AIUtils import \
    sortJson, loadJsonFromFile, natural_key, makeOrdered
from echoprint_server import \
    load_inverted_index, query_inverted_index, \
    parsed_code_streamer, parsing_code_streamer, \
    create_inverted_index, decode_echoprint

class queryTypes(object):
    """Enum for the types of queries we can use to retrieve data.
    Choices are:
    jaccard
    set_ints
    sinlfs
    jaccard_frequent
    set_int_frequent
    sinlfs_frequent
    total_frequencies
    """
    jaccard = "jaccards"
    set_ints = "set_ints"
    sinlfs = "sinlfs"
    jaccard_frequent = "jaccard_frequent"
    set_int_frequent = "set_int_frequent"
    sinlfs_frequent = "sinlfs_frequent"
    total_frequencies = "total_frequencies"

def matchDecodes(prints, invertedIndex, startTime, interval, duration, queryType):
    jsons = getTimeChunks(prints, startTime, duration)
    scores = []
    total_frequencies = {}
    retDict  = {}
    for js in jsons:
        for codes in decode_echoprint(str(js["code"])): #must be str. json lib imports as Unicode, but echolib will fail on that
            if queryType == queryTypes.jaccard: scores.append(query_inverted_index(codes, invertedIndex, 'jaccard'))
            elif queryType == queryTypes.setInt: scores.append(query_inverted_index(codes, invertedIndex, 'set_int'))
            elif queryType == queryTypes.sinfl: scores.append(query_inverted_index(codes, invertedIndex, 'set_int_norm_length_first'))
    sums, freqs = makeSumsAndFrequencies(scores, total_frequencies)
    retDict["sums"] = sums
    retDict["frequencies"] = freqs
    return retDict

def MakeTimings(printsFiles, invertedIndex, queryType=queryTypes.jaccard, duration=60, interval=5):
    whichToGet = queryType
    for echo in printsFiles:
        baseDir = os.path.dirname(echo)
        echoTimings = makeEpisodeTiming(echo, invertedIndex, queryType, duration, interval)
        with open(os.path.join(baseDir, "timings.txt"), 'w') as f:
            f.writelines("\n".join(echoTimings))
    return 0

def makeEpisodeTiming(echofile, invertedIndex, queryType, duration, interval):
    form = "{0}{1}{2}"
    prints = loadJsonFromFile(echofile)
    timings = []
    for i in range(len(prints)):
        formed = ""
        ival = i*interval
        value = matchDecodes(prints, invertedIndex, ival, interval, duration, queryType)#TODO map DoStuff from averages.py
        first = str(datetime.timedelta(seconds=ival+duration))
        third = value["sums"][0][1]
        if(third < confidenceMap(queryType)):
            formed = form.format(first, "","")
        else:
            second = ""#IndexNumberToName(...) #TODO this function DNE yo
            formed = form.format(first.ljust(15),second.ljust(55),third)
        timings.append(formed)
    return timings
    
#Utility Section
def getTimeChunks(echoPrints, start, duration):
    form = "cut_{0}_{1}.flac"
    #get the index of the first decode we want
    sj = [x for x in echoPrints if x["metadata"]["filename"].endswith(form.format(str(start), str(start+duration)))]
    return sj

def confidenceMap(qtype):  
    """Our hueristic confidence for whether a song was "matched" """
    confidence_jaccard = 0.007
    confidence_setInts = 22
    confidence_sinlfs = 0.06
    confidence_jaccardFreq = 1
    confidence_setIntsFreq = 1
    confidence_sinlfsFreq = 1
    confidence_totalFreq = 1
    confidence = 0
    if qtype is queryTypes.jaccard:
        confidence = confidence_jaccard
    elif qtype is queryTypes.set_ints:
        confidence = confidence_setInts
    elif qtype is queryTypes.sinlfs:
        confidence = confidence_sinlfs
    elif qtype is queryTypes.jaccard_frequent:
        confidence = confidence_jaccardFreq
    elif qtype is queryTypes.set_int_frequent:
        confidence = confidence_setIntsFreq
    elif qtype is queryTypes.sinlfs_frequent:
        confidence = confidence_sinlfsFreq
    elif qtype is queryTypes.total_frequencies:
        confidence = confidence_totalFreq
    return 0#confidence
def makeSumsAndFrequencies(scores, totalFrequencies):
    sums = {}
    frequencies = {}
    for result in scores:
        for lst in result:
            subi = lst["index"]
            if subi in totalFrequencies:
                totalFrequencies[subi] += 1
            else:
                totalFrequencies[subi] = 1
            if subi in sums:
                sums[subi] += lst["score"]
                frequencies[subi] += 1
            else:
                sums[subi] = lst["score"]
                frequencies[subi] = 1
    return (makeOrdered(sums), makeOrdered(frequencies))
#Main
def main():
    OK = True
    parser = argparse.ArgumentParser()
    parser.add_argument("indexes", help="Compiled index (.bin) to match decoded echoprints against")
    parser.add_argument("echos", help="Input directory of echoprints to match")
    args = parser.parse_args()
    
    #Error collection for mistyped or invalid input
    Errors = []
    if not os.path.exists(args.indexes):
        Errors.append("Error - Index directory path \"{0}\" does not exist. Please enter a valid path and try again.".format(args.indexes))
        OK = False
    if not os.path.exists(args.echos):
        Errors.append("Error - Echprints directory path \"{0}\" does not exist. Please enter a valid path and try again.".format(args.echos))
        OK = False
    if not OK:
        for error in Errors:
            print(error)
        return 1

    #Getting episode files
    printsFiles = []
    for path,dirs,files in os.walk(args.echos):
        for d in dirs:
            dir = os.path.join(path,d)
            pjson = os.path.join(dir, "prints.json")
            if os.path.exists(pjson):
                printsFiles.append(pjson)

    #Creating the inverted index and the songToIndex namelist
    indexList = []
    nameIndex = []
    for path,dirs,files in os.walk(args.indexes):
        for f in files:
            if(f.endswith(".bin")):
                indexList.append(os.path.join(path,f))
            elif(f.endswith(".json")):
                nameIndex.append(os.path.join(path, f))
    print("Using the following indexes:")
    for i in indexList:
        print(os.path.basename(i))
    invertedIndex = load_inverted_index(indexList)
    #Create Timings
    MakeTimings(printsFiles, invertedIndex, queryType=queryTypes.jaccard)
    
    return 0

if __name__ == "__main__":
    main()