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

# TODO Manually emending sign readings will
# increase accuracy for identification of
# some commodities. Will require a sound list
# of equivalences. There is a possible list
# at http://etcsl.orinst.ox.ac.uk/edition2/signlist.php
# but we should contact Steve Tinney of the
# ePSD for permissions to use.
# 
# For now, just map zi3 -> zid2 as proof of concept:
sign_substitutions = {"zi3":"zid2"}
def substitute( sign ):
    if sign in sign_substitutions:
        return sign_substitutions[ sign ]
    return sign

# Determinatives selected based on ePSD definitions,
# personal experience, and 
# https://personal.sron.nl/~jheise/signlists/determin.html
commodity_determinatives = set([
        "gesz",     # wood
        "gisz",     # wood, alternate spelling
        "gi",       #reed
        "urudu",    #metal
        "tug2",     # cloth
        "ku6",      # fish
        #"sza:gan", # TODO pig, or a kind of pot/jar? both seem commodity-like
        "szagan",   # ^ same
        "sza",      # ^ same
        "gan",      # ^ same
        "sze3",     # wood, cf {sze3}szer7 = {gesz}szer7
        "zid2",     # grains
        "zi3",      # grains, alternate name for zid2
        "sar",      # plant
        #"ninda",   # TODO should be bread? or pole? ePSD not clear. cf nindaxDU 
        #"munus",   # TODO woman. likely more indicative of a name? check how precise this rule is
        #"da",      # TODO only occurs in banda3{da}, looking like a phonetic complement more than a determinative
        #"sza",     # TODO only with (asz){sza}
        "muszen",   # bird 
        #"gada",    # TODO meaning?
        "kusz",     # leather
        "dug",      # pottery
        #"ga2",     # TODO meaning?
        #"an",      # TODO meaning?
        #"ur3", # TODO only in dur9{ur3} "donkey". Looks again like phonetic complement. Are these animals being counted in the text?
        "ha",       # tree? Looks like phonetic complement which is only used (in Girsu texts) for {ha}har-ra-na
        "na4",      # stones
        "gu4",      # cattle
        "u2",       # plant
        ])

Entry = make_dataclass("Entry",
        [
            ("count",dict),
            ("words",list)
        ], defaults=[
            None,
            []
        ]) 
def new_entry():
    entry = Entry()
    entry.words = []
    return entry

############################################
# Process each text and annotate the words
# which are likely to represent counted objects:
#
def commodify( text ):

    # Standardize notation: asz@c -> asz, ASZxDISZ@t -> ASZxDISZ, etc
    # These represent curved/flat/rotated/variant sign forms
    # but we care about a more granular level of detail
    text = [ re.sub("@[a-zA-Z]*","",word) for word in text ]
    text = list(map(substitute,text))

    entries = []
    entry = new_entry()
    for word, counts in segment.segment( text ):
        # TODO Idea: limit to the first n words after the digit?
        # Later information tends to represent recipients,
        # festivals, explanations, etc. 
        if word == "x" or word == "...":
            entry.words += [word]
            #print( word, end=' ' )
            continue

        if counts is not None and len(counts) > 0:
            #print()
            #print( word, end=' ' )
            # This is a numeral:
            entries.append( entry )
            entry = new_entry()
            entry.count = {"string":word,"readings":counts}
            continue

        # If a word contains one of the commodity determinatives,
        # (or it's tagged as a noun,)
        # mark it as a commodity.
        #
        # TODO Focus refinements on this part of the script:
        if any( "{%s}"%(det) in word for det in commodity_determinatives ):
                #or any(defn[1] == "NN" for defn in dictionary[word]) \

            # For now just use CLAWS-style _COM tag:
            #print( "%s_COM"%(word), end=' ' )
            entry.words += ["%s_COM"%(word)]
            pass

        else:
            entry.words += [word]
            # We can use fuzzy string matching to identify known 
            # words with extra morphology attached, but this is
            # slow and low-precision. Ideally we want proper automated
            # stemming/morphological parsing.
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

    entries.append( entry )
    entries = [ entry for entry in entries if not (entry.count is None and entry.words == [])]
    return entries

if __name__ == "__main__":
    # *_COM -> num string -> number of occurrences
    counts_by_commodity = defaultdict(lambda:defaultdict(int))
    # *_COM -> [values]
    values_by_commodity = defaultdict(list)
    # (*_COM, *_COM) -> number of cooccurrences
    collocation_counts = defaultdict(int)

    commodified_texts = []
    for text in data.girsu:
        commodified_texts.append( commodify( text ) )

    for entries in commodified_texts:
        if len(entries) > 5 and len(entries) < 50:
            for entry in entries:
                
                if entry.count is not None:
                    count = entry.count["string"]
                    values = entry.count["readings"]
                else:
                    count, values = "", []

                for word in entry.words:
                    if word.endswith("_COM"):
                        # Don't count broken commodities 
                        # like ...{ku6}:
                        if '...' in word:
                            continue
                        # TODO How to handle unreadable counts? 
                        # Probably count every instance of the commodity,
                        # so that people can accurately say such-and-such
                        # occurs N times in the corpus, but omit "none"
                        # from the list of values? 
                        word = word.replace( "_COM", "" )
                        counts_by_commodity[ word ][ count ] += 1
                        # TODO How do we want to resolve ambiguous values?
                        # As baseline, just pick the first possible value:
                        if values != []:
                            values_by_commodity[ word ].append( values )

            for i in range(len(entries)):
                for j in range(i+1,len(entries)):
                    for word_i in entries[i].words:
                        if not word_i.endswith( "_COM" ):
                            continue
                        for word_j in entries[j].words:
                            if not word_j.endswith( "_COM" ):
                                continue
                            # dict can only store tuple values
                            # for consistency, sort the keys
                            # and provide and accessor that 
                            # sorts queries likewise
                            key = tuple(sorted([
                                word_i.replace("_COM",""), 
                                word_j.replace("_COM","")]))
                            collocation_counts[ word_i, word_j ] += 1
    all_objects = counts_by_commodity.keys()

    output_json = {
            "counts_by_commodity": dict(counts_by_commodity),
            "values_by_commodity": dict(values_by_commodity),
            "all_objects": list(all_objects),
        }

    # TODO Some refinements needed: is {gesz}RU the same as {gesz}RU-ur-ka minus morphology?
