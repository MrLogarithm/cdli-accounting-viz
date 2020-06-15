#!/bin/python
# Usage: ./wordlist.sh | python analyse.py

from nltk.corpus import wordnet as wn

import json
import segment
import convert
import data
import numpy as np
import re
from fuzzywuzzy import fuzz
from collections import defaultdict
from recordclass import make_dataclass

# Load dictionary for use in making annotations:
dictionary = np.load( "dict/epsd.npz", allow_pickle=True )["dictionary"].item()

# For now, just map zi3 -> zid2 as proof of concept:
sign_substitutions = {"zi3":"zid2"}
def substitute( sign ):
    if sign in sign_substitutions:
        return sign_substitutions[ sign ]
    return sign

def get_hypernyms( word ):
    all_hypernyms = wn.synsets( word )
    # limit to noun readings:
    all_hypernyms = [h for h in all_hypernyms if ".n." in str(h)]
    i = 0
    while i < len(all_hypernyms):
        hypernyms = all_hypernyms[i].hypernyms()
        all_hypernyms += hypernyms
        i += 1
    all_hypernyms = set(all_hypernyms)
    return all_hypernyms

def is_commodity_synset( word, synsets ):
    units = [
            "asz", "ban2", "barig", "bur3", "danna", "disz",
            "dug", 
            #"esz2", # flour, rope
            "esze3", "gan2", "gesz2", "geszu",
            #"gi", 
            "gin2", "gu2", "gur", "guru7", "iku", "kusz3",
            #"ninda", 
            "sar", "sila3", "szar2", "szargal", 
            #"sze",
            "u", "usz",
            "la2", # subtraction - not a unit but part of the number #
            # TODO kur2 Unit amount?
            # TODO kusz3 Unit amount?
            "{ninda}nindax(DU)", # apparently another spelling for ninda
        ]
    blacklist_words = [
            "lugal", # king
            "geme2", # worker (human, not animal)
            "sa", # bundle TODO this implies the following word is a commodity, often eg turnips
            # TODO dag "pot" also implies following is commodity, but sometimes occurs on its own
            # TODO sa2-du11 "offering" implies following is com
            # TODO nig2-du3-a "string" of fruit, following word
            # todo munus-me person - ration?
            "ge6", # black - missing from dictionary
            "x",
            "babbar2", # white
            "sag", # TODO many meanings - some disambiguation? #
            "dar-ra", # split - adjective modifier
            "za-na", # TODO meaning?
            "gu-la2", # large/gal TODO a unit? word order is wrong for it to be "large garlic" in gu-la2 szum2 szuh5-ha
            "u4", # days - these are the object being counted but are they relevant?
        ]
    whitelist_words = [
            "kas", # often written in place of kasz "beer"
            #"dam", # TODO spouse, but sometimes looks like a female slave?
            "gu4", # cattle
            #"igi-nu-du8", # blind - counted as objects, or recipients of rations?
            # nu-siki orphan - orphaned animals or people?
            # nita-me male - person?
            # en-ku3 - person - implied ration?
            "tug2",
            "ga'ar", # cheese
            "szuku", # ration
            "ud5", # goat
        ]
    blacklist_syns = [
            "person."
        ]
    whitelist_syns = [
            "implement.", 
            'food.', 
            'plant.', 
            'material.', 
            'animal.', 
            'tool.', 
            "stone.", 
            "rock.", 
            'tree.', 
            'commodity.', 
            'clothing.', 
            'skin.', 
            'hair.', 
            'musical_instrument.', 
            'wood.'
        ]
    if word in units:
        return False, ["UNIT"]

    if word in blacklist_words:
        return False, []

    if word in whitelist_words:
        return True, ["WHITELIST"]

    matches = [ synset for synset in synsets if any(term in str(synset) for term in whitelist_syns) ]
    bad_matches = [ synset for synset in synsets if any(term in str(synset) for term in blacklist_syns) ]
    if matches != []:
        return True, matches
    if bad_matches != []:
        return False, bad_matches
    return False, []

com_instances = 0
num_coms = 0
num_det = 0

num_neg = 0
neg_inst = 0

import sys
for word in sys.stdin:
    try:
        #count, word=word.lower().strip().split(" ")
        count, word=word.strip().split(" ")
    except:
        continue
    if word in dictionary:
        is_com = False
        is_neg = False
        defs = list(dictionary[word])
        for def_,pos in defs:
            def_ = def_.replace("?","")
            com, syns = is_commodity_synset( word, get_hypernyms(def_) )
            print((" "*31)+"\t{0} {1}".format(def_,pos,))
            print((" "*31)+"\t{0}".format(
                  (com, syns)
                ))
            if com:
                is_com = True
            elif syns != []:
                is_neg = True
        print()
        print("{0:5} {1:25} {2}".format(count, word, is_com))
        if is_com:
            #print(word,"is com")
            if "{" in word:
                num_det += 1
                print("*"*100)
            num_coms += 1
            com_instances += int(count)
        elif is_neg:
            num_neg += 1
            neg_inst += int(count)
    else:
        print(word,"not in dictionary")
        pass
        #print(dictionary[word] if word in dictionary else word)

            #if dictionary[word] == set():
                #print(word, [
                    #key for key in dictionary 
                    #if key != word 
                    #and fuzz.ratio(word,key) > 90
                    #])
                #print( "%s"%(word), end=' ' )
                #pass
            #else:
                #print( "%s"%(word), end=' ' )
                #pass
print("found", num_coms, 'non det:', num_coms - num_det, "instances:",com_instances,"not com",num_neg,'neg inst',neg_inst)
