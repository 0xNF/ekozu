#!/usr/bin/env python
# encoding: utf-8
import json
import os
from sys import argv

fmaps = {
    "r1":"/mnt/c/Users/Djori/Documents/projects/ekozu/testData/geass/tracepaths/r1_tracks_1.json",
    "r2":"/mnt/c/Users/Djori/Documents/projects/ekozu/testData/geass/tracepaths/r2_tracks_1.json"
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
                #if(item["tag"] in jobjtags):
                    #print("Tag Existed! {0}, replaced with {1}.".format(str(item["tag"]), str((item["tag"]+maxTag))))
                #    item["tag"] += maxTag
                jobj.append(item)
                #jobjtags.append(item["tag"])
                #x["metadata"]["filename"]
    jj = jobj#sorted(jobj, key=lambda x: x["tag"], reverse=True)
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


        #print("\n".join([x["metadata"]["filename"] for x in mergeIndexs(files)]))

if __name__ == "__main__":
    main()