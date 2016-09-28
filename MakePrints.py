import sys
import os
import subprocess
import argparse

#...

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('indir', type=str, help="audio file to split")
    parser.add_argument('duration', type=int, help="time in seconds for each chunk to be")
    parser.add_argument('out', type=str, help="output directory for the chunked files")
    args = parser.parse_args()


if __name__ == "__main__":
    main()