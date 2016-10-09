#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import json
import os,sys
import shutil
import argparse
import subprocess
import NameFromIndex
import collectAverages
from RollingSplit import split
from MakePrints import makeWithPath, sortAndWrite
from AIUtils import \
    sortJson, loadJsonFromFile, natural_key
from echoprint_server import \
    load_inverted_index, query_inverted_index, \
    parsed_code_streamer, parsing_code_streamer, \
    create_inverted_index, decode_echoprint

def MakeTimings(episodeDir, indexDir):
    return 0

def main():
    return 0

if __name__ == "__main__":
    main()