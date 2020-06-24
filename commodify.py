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

##################################################
# Sign substitutions:

# TODO Manually emending sign readings will
# increase accuracy for identification of
# some commodities. Will require a sound list
# of equivalences: perhaps based on the list
# from the Nuolenna project?
# https://github.com/tosaja/Nuolenna/blob/master/sign_list.txt
# 
# For now, just map some manually identified cases as
# proof of concept:
sign_substitutions = {
        #'sign in the dictionary':'sign in the corpus',
        "zid2":"zi3",
        "kug":"ku3",
        "ku3":"kug",
        "ERIN2":"ERIM",
        }

def substitute( sign ):
    if sign in sign_substitutions:
        yield sign_substitutions[ sign ]
        return
    else:
        for s in sign_substitutions:
            yield re.sub("(^|-|\()"+s+"(-|$|\))","\\1"+sign_substitutions[s]+"\\2",sign)
    return 

# Emend the dictionary:
words = list(dictionary.keys())
for word in words:
    for sub in substitute( word ):
        dictionary[ sub ] = dictionary[word]

##################################################
# Determinative rules:

# Determinatives selected based on ePSD definitions,
# personal experience, and 
# https://personal.sron.nl/~jheise/signlists/determin.html
commodity_determinatives = set([
        "dug",      # pottery
        "gan",      # pig 
        "gesz",     # wood
        "gisz",     # wood, alternate spelling
        "gi",       #reed
        "gu4",      # cattle
        "ha",       # tree? Looks like phonetic complement which is 
                    # only used (in Girsu texts) for {ha}har-ra-na
        "ku6",      # fish
        "kusz",     # leather
        "muszen",   # bird 
        "na4",      # stones
        "sar",      # plant
        "sza:gan",  # pig
        "szagan",   # pig
        "sza",      # pig 
        "sze3",     # wood, cf {sze3}szer7 = {gesz}szer7
        "tug2",     # cloth
        "u2",       # plant
        "uruda",    # metal
        "urudu",    # metal
        "zi3",      # grains, alternate name for zid2
        "zid2",     # grains
        #"ninda",   # Usage seems restricted to {ninda}nindax(DU) 
                    # where it appears to be a length measurement.
        #"munus",   # TODO woman. likely more indicative of a name? 
                    # check how precise this rule is
        #"da",      # TODO only occurs in banda3{da}, looking like 
                    # a phonetic complement more than a determinative
        #"sza",     # TODO only with (asz){sza}
        #"gada",    # TODO meaning?
        #"ga2",     # TODO meaning?
        #"an",      # TODO meaning?
        #"ur3",     # TODO only in dur9{ur3} "donkey". Looks again like 
                    # phonetic complement. 
        ])

# Mutable alternative to namedtuple:
Entry = make_dataclass("Entry",
        [
            ("counts",list),
            ("words",list)
        ], defaults=[
            [],
            []
        ]) 

def new_entry():
    entry = Entry()
    # Initialize these as empty lists:
    # otherwise python makes a shallow
    # copy and all entries end up sharing
    # the same list of words:
    entry.counts = []
    entry.words = []
    return entry

def label_wordlist( words ):
    """
    words:      a list of words to label as commodities
    returns:    the input list, with commodities labeled
                by _COM, modifiers such as adjectives labeled
                by _MOD, and vessels labeled as _VES
    """
    if words == []:
        return words 

    # Don't label dates:
    if words[0] in set(["mu", "u4", "iti"]):
        return words

    # If this line is a total, we should ignore it to avoid double counts
    # "dur" can also mark a total, or be a counted object
    if words[0] in set(["szunigin", "gu2-an-sze3", "szu-nigin2"]): 
        words += ["TOTAL"]
    # Donors and explanatory information:
    #if words[0] in set(["ki", "giri3"]):
        #return words
    # If there is no count we assume (perhaps incorrectly)
    # that nothing is being counted in this line:
    if "###" not in words:
        return words

    # Now we annotate words with various features
    # We will use these features to manually decide
    # what is a commodity, but moving forward we can
    # add more features and train a real ML model:
    features = [[] for _ in words]
    for i,word in enumerate(words):

        FEAT_NONE = 0
        FEAT_COM  = 1
        FEAT_PERS = 2
        FEAT_ADJ  = 3
        FEAT_VES  = 4

        # DETERMINATIVES
        if any( "{%s}"%(det) in word for det in commodity_determinatives ):
            #or any(defn[1] == "NN" for defn in dictionary[word]) \
            features[i].append( FEAT_COM )
        else:
            features[i].append( FEAT_NONE )

        # SYNSETS
        features[i].append( FEAT_NONE )
        if word in dictionary:
            # Check all definions of the word until one of them
            # gives us evidence to make a decision:
            for defn, POS in dictionary[word]:
                defn = defn.replace("?","")
                # Does this definition represent a commodity?
                is_com, evidence = semantic.is_commodity_synset( 
                        word, 
                        semantic.get_noun_hypernyms( defn )
                    )
                if is_com:
                    if any( "vessel" in str(synset) for synset in evidence):
                        features[i][-1] = FEAT_VES
                    else:
                        features[i][-1] = FEAT_COM
                    break
                elif not is_com and evidence != []:
                    if evidence == "person":
                        features[i][-1] = FEAT_PERS
                    elif evidence == "vessel":
                        features[i][-1] = FEAT_VES
                    elif evidence == "mod":
                        features[i][-1] = FEAT_ADJ
                    elif isinstance( evidence, list ) and type( evidence[0] ).__name__ == "Synset":
                        if any( "person" in str(synset) for synset in evidence ):
                            features[i][-1] = FEAT_PERS
                        else:
                            features[i][-1] = -1
                    else:
                        features[i][-1] = -1
                    break
        else:
            # If word is not in the dictionary, don't pass a list of synsets
            is_com, evidence = semantic.is_commodity_synset( word, None )
            if is_com:
                features[i][-1] = FEAT_COM



    # Use the features from the last section to 
    # label the words in the input list:
    maybe_ration = False
    # If two commodity-like items occur within this many words
    # of one another, the second will be labeled as a modifier.
    # This helps with cases like siki udu, where udu and siki
    # can both be commodities but udu here acts as a modifier.
    mod_proximity_threshold = 3
    for i in range(len(words)):
        if words[0] in set(["ki-la2-bi"]) and words[i] == "na4":
            continue
        context = words[max(0,i-mod_proximity_threshold):i]
        if features[i][0] == FEAT_COM:
            # This check helps avoid labeling modifiers
            # as commodities: e.g. in zi3 sig15, only
            # label zi3, as we would in e.g. ku6 dar-ra
            if i>0 and any( "_" in w for w in context ):
                words[i] += "_MOD"
            else:
                words[i] += "_COM"
        elif features[i][1] == FEAT_VES:
            words[i] += "_VES"
        elif features[i][1] == FEAT_COM:
            if i>0 and any( "_" in w for w in context):
                words[i] += "_MOD"
            else:
                words[i] += "_COM"
        elif features[i][1] == FEAT_ADJ:
            # If this entry only contains one word and that word looks
            # like an adjective/modifier, we instead count it as a 
            # commodity: helps with e.g. mun "salt" which usually modifies
            # a fish (ku6 mun) but can also be counted on its own.
            if len([w for w in words if w != '###']) == 1 or all([features[i][1]==FEAT_ADJ for i in range(len(words)) if words[i]!='###']):
                if i>0 and any( "_" in w for w in context):
                    words[i] += "_MOD"
                else:
                    words[i] += "_COM"
            else:
                words[i] += "_MOD"
        elif features[i][1] == FEAT_PERS:
            # If this is a person, we infer that 
            # there may be an implicit ration:
            maybe_ration = True
    # If there is a commodity in the entry, then
    # the person is probably an owner or recipient.
    # If there is no commodity, then there is probably
    # an implicit ration:
    if maybe_ration:
        if not any( "_COM" in w for w in words ):
            words.append( "implied_ration?" )

    return words

############################################
# Process each text and annotate the words
# which are likely to represent counted objects:
#
def commodify( text ):

    entries = []
    entry = new_entry()

    # Record distance from the preceding number: 
    # most commodities occur within 3 tokens of the
    # numeral
    dist_from_numeral = 0
    # Have we found a commodity in this entry yet?
    found_com = False
    
    if not isinstance( text, list ):
        text = [ re.sub("@[a-zA-Z]*","",word) for word in text.strip().split(" ") ]
        text = segment.segment( text )
    else:
        # Standardize notation: asz@c -> asz, ASZxDISZ@t -> ASZxDISZ, etc
        # These represent curved/flat/rotated/variant sign forms
        # but we care about a more granular level of detail
        text = [ [ re.sub("@[a-zA-Z]*","",word) for word in line ] for line in text ]
        text = sum([ segment.segment( line ) for line in text ],[])

    for entry_ in text:

        entry = new_entry()

        for string, counts in entry_:
            if counts is not None:
                #entry.words = label_wordlist( entry.words )
                #entries.append( entry )
                #entry = new_entry()
                entry.counts.append( {"string":string, "readings":counts} )
                entry.words.append( "###" )
            else:
                entry.words.append( string )
        entry.words = label_wordlist( entry.words )
        entries.append( entry )

    # Tag and append the final entry:
    #entry.words = label_wordlist( entry.words )
    #entries.append( entry )
    entries = [ entry for entry in entries if not (entry.counts == [] and entry.words == [])]
    return entries

def commodify_whole_corpus():
    # *_COM -> num string -> number of occurrences
    counts_by_commodity     = defaultdict(lambda:defaultdict(int))
    # *_COM -> [values]
    values_by_commodity     = defaultdict(list)
    # (*_COM, *_COM) -> number of cooccurrences
    collocation_counts = defaultdict(int)

    commodified_texts = []
    for text in data.girsu_lined:
        commodified_texts.append( commodify( text ) )
        #for e in commodified_texts[-1]:
            #print(e.words)

    for entries in commodified_texts:
        for entry in entries:
                
            #if entry.words.count("###") > 1:
                #continue

            if entry.counts != []:
                count = entry.counts[0]["string"]
                values = entry.counts[0]["readings"]
            else:
                count, values = "", []

            for i,word in enumerate(entry.words):
                if word.endswith("_COM"):
                    # Don't count broken commodities 
                    # like ...{ku6}:
                    if '...' in word:
                        continue

                    # In cases like udu_COM nita_MOD,
                    # retrieve the modifier:
                    commodity = word#.replace("_COM","")
                    modified  = [commodity]
                    for w in entry.words[i+1:]:
                        if w.endswith("_MOD"):
                            modified.append(w)#.replace("_MOD",""))
                        if w.endswith("_COM") or w == "###":
                            break

                    # TODO How to handle unreadable counts? 
                    # Probably count every instance of the commodity,
                    # so that people can accurately say such-and-such
                    # occurs N times in the corpus, but omit "none"
                    # from the list of values? 

                    # JSON keys can't be tuples:
                    key = ' '.join(modified)
                    counts_by_commodity[ key ][ count ] += 1
                    # TODO How do we want to resolve ambiguous values?
                    # As baseline, just pick the first possible value:
                    if values != []:
                        values_by_commodity[ key ].append( values )

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
                        key = ' '.join(sorted([
                            word_i.replace("_COM",""), 
                            word_j.replace("_COM","")]))
                        collocation_counts[ key ] += 1
    all_objects = sorted(list([re.sub('_[A-Z]{3}', '', k) for k in counts_by_commodity.keys()]))
    output_dictionary = {
            word:list(dictionary[word])[0][0] 
            for word in all_objects
            if len(dictionary[word]) > 0
        }

    output_json = {
            "counts_by_commodity": dict(counts_by_commodity),
            "values_by_commodity": dict(values_by_commodity),
            "collocation_counts":  dict(collocation_counts),
            "all_objects": all_objects,
            "dictionary":output_dictionary,
        }

    return output_json

if __name__ == "__main__":
    output_json = commodify_whole_corpus()

    outfile = open("commodities.json", "w")
    json.dump( output_json, outfile, indent=2 )
    outfile.close()
