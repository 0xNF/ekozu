import sys
import os
import subprocess
import argparse

def getAudioLength(fname):
    args = ("ffprobe", "-show_entries", "format=duration", "-loglevel", "quiet", "-i", fname)
    output = subprocess.check_output(args)
    durStr = output.split('\n')[1].split("duration=")[1]
    dur = int(float(durStr))
    return dur

def getTimes(totalseconds, duration):
    times = []
    for i in range(0, totalseconds):
        start = i
        end = i+duration
        if end > totalseconds:
            break
        else:
            times.append((start,end))
    return times

def split(fname, duration, outdir):
    ftype = fname.split('.')[-1]
    abspath = os.path.join(os.path.abspath(outdir), "splits")
    try:
        if not os.path.exists(abspath):
            os.makedirs(abspath)
    except OSError:
        if exception.errno != errno.EEXIST or exception.errno == ENOTDIR:
            raise

    totalSeconds = getAudioLength(fname)
    times = getTimes(totalSeconds, duration)
    #Output updating vars
    counter = 0
    percent = 1/100.0
    blocks = int(len(times) * percent)
    print("Blocks: " + str(blocks))
    #Real work
    for time in times:
        outpath = os.path.join(abspath, "cut_{0}_{1}.flac".format(time[0], time[1]))
        args = ("ffmpeg", "-loglevel", "quiet", "-i", fname, "-ss", str(time[0]), "-to", str(time[1]), "-async", "1", outpath)
        if counter % blocks == 0:
            print(str(counter+0.0 * percent) + "%")
        counter+=1
        #print(args)
        subprocess.check_output(args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help="audio file to split")
    parser.add_argument('duration', type=int, help="time in seconds for each chunk to be")
    parser.add_argument('out', type=str, help="output directory for the chunked files")
    args = parser.parse_args()
    split(args.filename, args.duration, args.out)


if __name__ == "__main__":
    main()