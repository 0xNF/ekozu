#!/usr/bin/env python
# encoding: utf-8
import json
import os
from sys import argv

fmaps = {
    "r1":"/mnt/c/Users/Djori/Documents/projects/ekozu/testData/geass/tracepaths/r1_tracks_1.json",
    "r2":"/mnt/c/Users/Djori/Documents/projects/ekozu/testData/geass/tracepaths/r2_tracks_1.json",
    #r1
    "r1Ost1":'/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/tracepaths/CodeGeassR1OST1_song_results.json',
    "r1Ost2":'/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/tracepaths/CodeGeassR1OST2_song_results.json',
    "r1OpsEds":'/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/tracepaths/CodeGeassR1OpEdInserts_song_results.json',
    #r2
    "r2OpsEds":'/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/tracepaths/CodeGeassR2OpEdInserts_song_results.json',
    "r2Ost1":'/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/tracepaths/CodeGeassR2OST1_song_results.json',
    "r2Ost2":'/mnt/c/Users/Djori/Documents/projects/ekozu/code geass/tracepaths/CodeGeassR2OST2_song_results.json',
    #lit
    "lit":"/mnt/c/Users/Djori/Documents/projects/ekozu/Lost in Translation/tracepaths/LostInTranslationOST_song_results.json"
    }

def mergeIndexs(indexs):
    jobj = []
    jobjtags = []
    for idx in indexs:
        contents = ""
        with open(idx, 'r') as f:
            contents = "".join(f.readlines())
            jtemp = json.loads(contents)
            jtemp = sorted(jtemp, key=lambda x: x["metadata"]["filename"])
            maxTag = 0 if len(jobj) is 0 else len(jtemp)
            for item in jtemp:
                jobj.append(item)
    jj = jobj
    return jj

def getIndex(indexs, i):
    jobj = mergeIndexs(indexs)
    return jobj[i]

def NameFromIndex(files, index, fullPath=True):
    text = getIndex(files,index)["metadata"]["filename"]
    if fullPath:
        return text
    else:
        return os.path.basename(text)

def main():
    if len(argv) < 3:
        return
    else:
        files = []
        for arg in argv[2:]:
            files.append(fmaps[arg])
        if argv[1] == "print":
            print(mergeIndexs(files))
        else:
            idx = int(argv[1])
            print(NameFromIndex(files, idx))
if __name__ == "__main__":
    main()