#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import os
import sys
import subprocess
import argparse

def getAudioLength(fname):
    args = ("ffprobe", "-show_entries", "format=duration", "-loglevel", "quiet", "-i", fname)
    output = subprocess.check_output(args)
    durStr = output.split('\n')[1].split("duration=")[1]
    dur = int(float(durStr))
    return dur

def getTimes(totalseconds, duration, interval):
    times = []
    for i in range(0, totalseconds, interval):
        start = i
        end = i+duration
        if end > totalseconds:
            break
        else:
            times.append((start,end))
    return times

def split(fname, duration, interval, outdir, silent=False):
    ftype = fname.split('.')[-1]
    abspath = os.path.join(os.path.abspath(outdir), "splits")
    try:
        if not os.path.exists(abspath):
            os.makedirs(abspath)
    except OSError:
        if exception.errno != errno.EEXIST or exception.errno == ENOTDIR:
            raise
    totalSeconds = getAudioLength(fname)
    times = getTimes(totalSeconds, duration, interval)
    #Output updating vars
    total = len(times)
    point = total/100
    increment = total/20    
    fileFormatString = "cut_{0}_{1}.flac"
    #Real work
    for idx,time in enumerate(times):
        outpath = os.path.join(abspath, fileFormatString.format(time[0], time[1]))
        args = ("ffmpeg", "-loglevel", "quiet", "-i", fname, "-ss", str(time[0]), "-to", str(time[1]), "-async", "1", outpath)
        if not silent and idx % (5 * point) == 0:
            sys.stdout.write("\r[" + "=" * (idx / increment) +  " " * ((total - idx)/ increment) + "]" +  str(idx / point) + "%")
            sys.stdout.flush()
        subprocess.check_output(args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help="audio file to split")
    parser.add_argument('duration', type=int, help="time in seconds for each chunk to be")
    parser.add_argument("interval", type=int, help="time in seconds for the chunk intervals to be. ")
    parser.add_argument('out', type=str, help="output directory for the chunked files")
    args = parser.parse_args()
    split(args.filename, args.duration, args.interval, args.out)


if __name__ == "__main__":
    main()