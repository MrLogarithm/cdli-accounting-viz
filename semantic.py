#!/bin/python
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

def get_noun_hypernyms( word ):
    """
    word:       An English word
    returns:    A set of Synset objects representing the given
                word's hypernyms. Only returns noun synsets.
    """
    all_hypernyms = wn.synsets( word )
    # Limit to noun readings:
    all_hypernyms = [h for h in all_hypernyms if ".n." in str(h)]
    i = 0
    while i < len(all_hypernyms):
        hypernyms = all_hypernyms[i].hypernyms()
        all_hypernyms += hypernyms
        i += 1
    all_hypernyms = set(all_hypernyms)
    return all_hypernyms


def is_commodity_synset( word, synsets ):
    """
    word:       A Sumerian word
    synsets:    A set of Synsets representing the possible readings
                for this word.
    returns:    (is_com, evidence) A tuple where the first item is a boolean
                specifying whether the item is probably a commodity, and the
                second item is a summary of the evidence used to arrive at this
                conclusion. evidence can be a string specifying what kind of
                object the input represents ("mod", "vessel", "person") or a 
                list of synsets.
    """
    # List of words that are used as units, and should not be labeled as commodities:
    units = [
            "asz", "ban2", "barig", "bur3", "danna", "disz",
            "dug", 
            "esze3", "gan2", "gesz2", "geszu",
            "gin2", "gu2", "gur", "guru7", "iku", "kusz3",
            "sar", "sila3", "szar2", "szargal", 
            "u", "usz",
            "la2", # subtraction - not a unit but part of the number
            "{ninda}nindax(DU)", # another spelling for ninda
            #"ninda", # This can also represent bread; unlike the other
            # spelling this one is ambiguous
            #"sze", # barley, can be a counted object
            #"esz2", # flour, rope, can be counted
            #"gi",# reeds, can be counted
            "gu-la2", # sheaves
            "kusz3", # unit of length
            "kur2", # vessel size
        ]
    # List of words which may look like commodities based on their synsets,
    # but are not. The value in the dictionary should represent why they
    # aren't commodities: 
    #   mod: for adjectives and modifiers like mun ("salted"). Usually preceeded
    #        by a commodity.
    #   person: for words which represent people but may look like animals
    #           based on their synsets. Often implies a ration amount
    #   vessel: for words which represent containers or other aggregations
    #           of items. Usually followed by a commodity.
    #   "": for words which are not commodities, and carry no special information
    #       that can be used to help identify nearby words
    #   date: for words used in writing dates and durations
    blacklist_words = {
            "x":"", # broken sign, do not count as an object

            "a2":"", # "half-day's labor"
            "a-ra2":"", # times, as in a-ra2 1(disz)-kam the first time
            "ba":"", # "allot", precedes a name, usually after a field area
            "ba-ug7-ge":"", # die, the verb, not the noun
            "giri3":"", # through, from, via
            "ma2":"", # boat
            "ma2-gur8":"", # boat
            "sag":"", # TODO has many meanings, some WSD might be helpful
            "si-i3-tum":"", #remainder
            "us2-sa":"",

            "dub-sar":"person", # scribe, the person not the implement
            "geme2":"person", # worker (human, not animal)
            "igi-nu-du8":"person", # blind 
            "lugal":"person", # king
            "nita-me":"person",#male, person?
            
            "dag":"vessel", # pot
            "nig2-du3-a":"vessel", # "string" of fruit, following word is a commodity
            "sa":"vessel", # bundle, implies the following word is a commodity, often eg turnips
            
            "babbar2":"mod", # white
            "dar-ra":"mod", # split - adjective modifier
            "gi":"mod", # reed - sometimes a unit, but counted in contexts like sa gi
            "ge6":"mod", # black - missing from dictionary
            "li":"mod", # oil, as in udu nita li
            "mun":"mod", # salt
            "murgu2":"mod", # shoulder/spine of fruit
            "na":"mod", # stone, used for denoting means of measurement
            "nim":"mod", # fly?
            "nita":"mod", # male, animal
            "nu-siki":"mod", # orphan, usually describes animals

            "mu":"date", # year
            "u4":"date", # days

            # TODO sa2-du11 "offering" implies following is commodity, but it is not a vessel
            # do we change the term "vessel" to something more generic?
            # TODO munus-me person - implies a ration? likewise nita-me and en-ku3
        }
    # Words which would not get labeled based on their synsets, but which
    # should be counted as commodities. Also useful for words which are
    # not in the dictionary:
    whitelist_words = [
            "am-ra", # beam, for a boat
            "ga'ar", # cheese
            "gu4", # cattle
            "kas", # often written in place of kasz "beer"
            #"dam", # TODO spouse, but sometimes looks like a female worker being counted. 
            "sze",
            "SZIM", # aromatic/perfume
            "szim",
            "szuku", # ration
            "tug2",
            "ud5", # goat
        ]
    # Words with any of these values in their synsets will not be counted as commodities:
    blacklist_syns = [
            "person.",
            "reservoir.",
        ]
    # Words with any of these values in their synsets will be counted as commodities:
    whitelist_syns = [
            "implement.", 
            'tool.', 
            'musical_instrument.', 

            'food.', 
            'plant.', 

            'material.', 
            'clothing.', 

            "metal", 
            "stone.", 
            "rock.", 

            'animal.', 
            'skin.', 
            'hair.', 

            'tree.', 
            'wood.',

            'vessel.',
            'container.',

            'commodity.', 
        ]

    if word in units:
        return False, ["UNIT"]

    if word in blacklist_words:
        return False, blacklist_words[word]

    if word in whitelist_words:
        return True, ["WHITELIST"]

    if synsets is None:
        return False, []

    # Check for matches in the synsets:
    matches = [ synset for synset in synsets if any(term in str(synset) for term in whitelist_syns) ]
    bad_matches = [ synset for synset in synsets if any(term in str(synset) for term in blacklist_syns) ]

    if matches != []:
        return True, matches
    if bad_matches != []:
        return False, bad_matches
    # If we have no rules that apply to this word, do not label 
    # it as a commodity, but return an empty evidence list so 
    # the caller knows the term is not blacklisted:
    return False, []
