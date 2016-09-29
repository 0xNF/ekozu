#!/usr/bin/env python
# encoding: utf-8
import json
import re

#Json utilities section
def sortJson(jobj, cmp, key):
    """ (dict/json, function, function) -> dict
    Sorts a JSON object / Dictionary by the given comparison function and key
    if no comparison is given, or comparison is None, defaults to a natural ordering
    """    
    cmp = cmp if cmp != None else natural_key
    return sorted(jobj, cmp=cmp, key=key, reverse=False)

#Natural sorting utility section
def __nat_alphaNumkey():
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    return lambda key: [ convert(c) for c in re.split('([0-9]+)',key) ] 

def __nat_compare(k):
    return __nat_alphaNumkey()(k)

def natural_sort(l): 
    return sorted(l, key = __nat_alphaNumkey())

def natural_key(x, y):
    matcher = re.compile("d+")
    x = __nat_compare(x)
    y = __nat_compare(y)
    if x == y:
        return 0
    elif x > y:
        return 1
    else:
        return -1      