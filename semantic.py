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
    blacklist_words = {
            "ba":"",# allot, precedes a name, usually after a field area
            "murgu2":"adj",# shoulder/spine of fruit
            "a2":"",#"half-day's labor"
            "lugal":"person", # king
            "geme2":"person", # worker (human, not animal)
            "sa":"bundle", # bundle TODO this implies the following word is a commodity, often eg turnips
            # TODO dag "pot" also implies following is commodity, but sometimes occurs on its own
            # TODO sa2-du11 "offering" implies following is com
            # TODO nig2-du3-a "string" of fruit, following word
            # todo munus-me person - ration?
            "ge6":"adj", # black - missing from dictionary
            "x":"",
            "babbar2":"adj", # white
            "sag":"", # TODO many meanings - some disambiguation? #
            "dar-ra":"adj", # split - adjective modifier
            "za-na":"", # TODO meaning?
            "gu-la2":"adj", # large/gal TODO a unit? word order is wrong for it to be "large garlic" in gu-la2 szum2 szuh5-ha
            "u4":"date", # days - these are the object being counted but are they relevant?
            "mu":"date",#year
            "mun":"adj", # TODO blacklist only when no other object
            "dub-sar":"person", # scribe, the person not the implement
            "ba-ug7-ge":"",
            "si-i3-tum":"", #remainder
            "a-ra2":"", #times, as in a-ra2 1(disz)-kam the first time
            "na":"adj", #stone, used for denoting means of measurement
            "li":"adj",#oil, as in udu nita li
            "nim":"adj",#fly?
            "nita":"adj",#male, animal
            "nita-me":"person",#male, person?
            "giri3":"",#through, from, via
            "nu-siki":"adj",
            "igi-nu-du8":"person", # blind 
            "us2-sa":"",
        }
    whitelist_words = [
            "kas", # often written in place of kasz "beer"
            #"dam", # TODO spouse, but sometimes looks like a female slave?
            "gu4", # cattle
            # nu-siki orphan - orphaned animals or people?
            # nita-me male - person?
            # en-ku3 - person - implied ration?
            "tug2",
            "ga'ar", # cheese
            "szuku", # ration
            "ud5", # goat
            "SZIM", # aromatic/perfume
            "szim",
            "sze",
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
            "metal", 
            "stone.", 
            "rock.", 
            'tree.', 
            'commodity.', 
            'clothing.', 
            'skin.', 
            'hair.', 
            'musical_instrument.', 
            'wood.',
            'vessel.'
        ]
    if word in units:
        return False, ["UNIT"]

    if word in blacklist_words:
        return False, blacklist_words[word] #["BLACKLIST"]

    if word in whitelist_words:
        return True, ["WHITELIST"]

    if synsets is None:
        return False, []

    matches = [ synset for synset in synsets if any(term in str(synset) for term in whitelist_syns) ]
    bad_matches = [ synset for synset in synsets if any(term in str(synset) for term in blacklist_syns) ]

    #if word == "ku3-bi":
        #print(word,synsets, matches, bad_matches)
    
    if matches != []:
        return True, matches
    if bad_matches != []:
        return False, bad_matches
    return False, []
