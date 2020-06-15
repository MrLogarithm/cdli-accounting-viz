from nltk.corpus import wordnet as wn
import json
import segment
import convert
import semantic
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
# of equivalences: perhaps based on the list
# from the Nuolenna project?
# https://github.com/tosaja/Nuolenna/blob/master/sign_list.txt
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
        #"sza:gan", # TODO pig, or a kind of pot/jar? 
                    # both seem commodity-like
        "szagan",   # ^ same
        "sza",      # ^ same
        "gan",      # ^ same
        "sze3",     # wood, cf {sze3}szer7 = {gesz}szer7
        "zid2",     # grains
        "zi3",      # grains, alternate name for zid2
        "sar",      # plant
        #"ninda",   # Usage seems restricted to {ninda}nindax(DU) 
                    # where it appears to be a length measurement.
        #"munus",   # TODO woman. likely more indicative of a name? 
                    # check how precise this rule is
        #"da",      # TODO only occurs in banda3{da}, looking like 
                    # a phonetic complement more than a determinative
        #"sza",     # TODO only with (asz){sza}
        "muszen",   # bird 
        #"gada",    # TODO meaning?
        "kusz",     # leather
        "dug",      # pottery
        #"ga2",     # TODO meaning?
        #"an",      # TODO meaning?
        #"ur3", # TODO only in dur9{ur3} "donkey". Looks again like 
                    # phonetic complement. 
        "ha",       # tree? Looks like phonetic complement which is 
                    # only used (in Girsu texts) for {ha}har-ra-na
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

def com_label( words ):
    if words == []:
        return words 

    features = [[] for _ in words]
    for i,word in enumerate(words):

        # DETERMINATIVES
        if any( "{%s}"%(det) in word for det in commodity_determinatives ):
            #or any(defn[1] == "NN" for defn in dictionary[word]) \
            features[i].append( 1 )
        else:
            features[i].append( 0 )

        features[i].append(0)
        FEAT_COM = 1
        FEAT_PERS = 2
        FEAT_ADJ = 3
        if word in dictionary:
            for defn, POS in dictionary[word]:
                defn = defn.replace("?","")
                is_com, evidence = semantic.is_commodity_synset( 
                        word, 
                        semantic.get_hypernyms( defn )
                    )
                if is_com:
                    features[i][-1] = FEAT_COM
                    break
                elif not is_com and evidence != []:
                    if evidence == "person":
                        features[i][-1] = FEAT_PERS
                    elif evidence == "adj":
                        features[i][-1] = FEAT_ADJ
                    elif isinstance( evidence, list ) and type( evidence[0] ).__name__ == "Synset":
                        features[i][-1] = -1
                        #if any( "person." in str(e) for e in evidence ):
                            # implicit ration?
                    else:
                        features[i][-1] = -1
                    break

    for i in range(len(words)):
        if features[i][0] == 1:
            words[i] += "_COM"
        elif features[i][1] == FEAT_COM:
            words[i] += "_COM"
        elif features[i][1] == FEAT_ADJ:
            # $mun$
            if len(words) == 1:
                words[i] += "_COM"

    return words

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

    # Record distance from the preceding number: 
    # most commodities occur within 3 tokens of the
    # numeral
    dist_from_numeral = 0
    # Have we found a commodity in this entry yet?
    found_com = False
    
    for word, counts in segment.segment( text ):

        dist_from_numeral += 1

        if word == "x" or word == "...":
            entry.words += [word]
            #print( word, end=' ' )
            continue

        elif counts is not None and len(counts) > 0:
            # This is a numeral (boundary between items)
            entry.words = com_label( entry.words )
            entries.append( entry )
            entry = new_entry()
            entry.count = {"string":word,"readings":counts}
            dist_from_numeral = 0
            found_com = False
            continue

        else:
            entry.words += [word]
        
    # Tag and append the final entry:
    entry.words = com_label( entry.words )
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
    print(output_json)

    # TODO Some refinements needed: is {gesz}RU the same as {gesz}RU-ur-ka minus morphology?
