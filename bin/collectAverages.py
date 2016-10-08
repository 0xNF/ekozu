#!/usr/bin/env python
# encoding: utf-8
import argparse
import json
import datetime
from AIUtils import loadJsonFromFile
from NameFromIndex import\
    fmaps, NameFromIndex
from echoprint_server import \
    load_inverted_index, query_inverted_index, \
    parsed_code_streamer, parsing_code_streamer, \
    decode_echoprint

def dostuff(startTime, interval, jaccard=True, setInt=True, sinfl=True):
    #Gets 1 minute (each chunk = 30 seconds, plus an additional 30 seconds = 1 minute) of echoprint slices from the episode list
    # jsons = getTimeChunk(episodePrints, startTime, duration)
    #print(startTime)
    jsons = getTimeChunk2(episodePrints, startTime)
    #decode and score the slices against the indexes
    jaccard_Scores = []
    set_int_Scores = []
    sinfl_Scores = []
    for js in jsons:
        for codes in decode_echoprint(str(js["code"])): #must be str. json lib imports as Unicode, but echolib will fail on that
            if jaccard: jaccard_Scores.append(query_inverted_index(codes, inverted_index, 'jaccard'))
            if setInt: set_int_Scores.append(query_inverted_index(codes, inverted_index, 'set_int'))
            if sinfl: sinfl_Scores.append(query_inverted_index(codes, inverted_index, 'set_int_norm_length_first'))

    total_frequencies = {}
    retDict  = {}
    if sinfl:
        sinlf_sums, sinlf_freqs = makeSumsAndFrequencies(sinfl_Scores, total_frequencies)
        retDict["sinlfs"] = sinlf_sums
        retDict["sinlf_frequent"] = sinlf_freqs
    if setInt: 
        set_int_sums, set_int_freqs = makeSumsAndFrequencies(set_int_Scores, total_frequencies)
        retDict["set_ints"] = set_int_sums
        retDict["set_int_frequent"] = set_int_freqs
    if jaccard: 
        jaccard_sums, jaccard_freqs = makeSumsAndFrequencies(jaccard_Scores, total_frequencies)
        retDict["jaccards"] = jaccard_sums
        retDict["jaccard_frequent"] = jaccard_freqs
    return retDict

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

def makeOrdered(iterable, reverse=True):
    srtd = sorted(iterable, key=iterable.get, reverse=reverse)
    return [(x,iterable[x]) for x in srtd]
def getTimeChunk(echoPrints, start, duration):
    #set filename format vars
    form = "cut_{0}_{1}.flac"
    end = start+60

    #get the index of the first decode we want
    sj = [x for x in echoPrints if x["metadata"]["filename"].endswith(form.format(str(start), str(start+30)))][0]
    idx = echoPrints.index(sj)

    #fill array of (#) duration decodes starting at the idx we found
    #Gives us one minute of total sound time
    jsons = []
    for i in range(idx-duration, idx):
        jsons.append(echoPrints[i])
    jsons.reverse()
    return jsons

def getTimeChunk2(echoPrints, start):
    form = "cut_{0}_{1}.flac"
    #get the index of the first decode we want
    sj = [x for x in echoPrints if x["metadata"]["filename"].endswith(form.format(str(start), str(start+60)))]
    return sj


#enum for the types of queries we can retrieve data by
class queryTypes(object):
    jaccard = "jaccards"
    set_ints = "set_ints"
    sinlfs = "sinlfs"
    jaccard_frequent = "jaccard_frequent"
    set_int_frequent = "set_int_frequent"
    sinlfs_frequent = "sinlfs_frequent"
    total_frequencies = "total_frequencies"

def confidenceMap(qtype):
    #Our hueristic confidence for whether a song was "matched"
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
#Main
def main():
    #load the episodes echoprints
    global episodePrints
    #episodePrints = loadJsonFromFile('/mnt/c/Users/Djori/Documents/projects/ekozu/testData/geass/episodetracks/r2_01/prints/prints.json')
    # episodePrints = loadJsonFromFile('/mnt/c/Users/Djori/Documents/projects/ekozu/testData/geass/episodetracks/r2_01/splits60-5/prints.json')
    episodePrints = loadJsonFromFile('/mnt/c/Users/Djori/Documents/projects/ekozu/Lost in Translation/episodes/Lost.in.Translation.2003.BluRay.720p.x264.YIFY.mkv/prints.json')

    #r2
    r2OpsEds = '/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/indexes/CodeGeassR2OpEdInserts_index.bin'
    r2Ost1 = '/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/indexes/CodeGeassR2OST1_index.bin'
    r2Ost2 = '/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/indexes/CodeGeassR2OST2_index.bin'
    #r1
    r1OpsEds = '/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/indexes/CodeGeassR1OpEdInserts_index.bin'
    r1Ost1 = '/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/indexes/CodeGeassR1OST1_index.bin'
    r1Ost2 = '/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/indexes/CodeGeassR1OST2_index.bin'

    #LIT
    lit = "/mnt/c/Users/Djori/Documents/projects/ekozu/Lost in Translation/indexes/LostInTranslationOST_index.bin"

    global inverted_index
    # inverted_index = load_inverted_index([r2Ost2, r2Ost1, r2OpsEds, r1Ost1, r1Ost2])
    inverted_index = load_inverted_index([lit])

    #formatting vars
    durationPerChunk = 60
    chunkInterval = 5
    allChunks = []
    chunkTotal = len(episodePrints)
    form = "{0}{1}{2}"
    songsByTheChunk = []
    #which of the different measurements to get. Switches the confidence type, also.
    whichToGet = queryTypes.jaccard

    #main loop    
    for i in range(chunkTotal):
        ival = i*chunkInterval#chunkInterval
        value = dostuff(ival, chunkInterval, jaccard=True, setInt=False, sinfl=False)[whichToGet]
        first = str(datetime.timedelta(seconds=ival+durationPerChunk))
        third = value[0][1]
        if(third < confidenceMap(whichToGet)):
            formed = form.format(first,"","")
        else:
            #second = NameFromIndex([fmaps["r2"],fmaps["r1"]], value[0][0], fullPath=False)
            #second = NameFromIndex([fmaps["r2Ost2"], fmaps["r2Ost1"], fmaps["r2OpsEds"], fmaps["r1Ost1"], fmaps["r1Ost2"]], value[0][0], fullPath=False)
            second = NameFromIndex([fmaps["lit"]], value[0][0], fullPath=False)
            formed = form.format(first.ljust(15),second.ljust(55),third)
        songsByTheChunk.append(formed)
    print("\n".join(songsByTheChunk))


if __name__ == "__main__":
    main()