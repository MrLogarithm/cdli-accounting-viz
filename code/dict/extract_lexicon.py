import os
import re
import numpy as np
from collections import defaultdict
from bs4 import BeautifulSoup

import nltk
import spacy

# If needed, download POS tagger:
nltk.download('averaged_perceptron_tagger')
spacy_tagger = spacy.load("en_core_web_sm")

dictionary = defaultdict(set)

def html_to_ascii( writing ):
    """
    Given a BeautifulSoup element containing the writing for
    this word, extract the writing in ATF format.

    writing:    A BeautifulSoup HTML element
    returns:    ATF equivalent of the input HTML element.
    """
    writing = str(writing)

    # Remove outermost tags:
    writing = writing[writing.index(">")+1:]
    writing = writing[: -1*writing[::-1].index("<") -1 ]
    
    # Rewrite special characters as ascii
    writing = re.sub("&amp;", "&", writing)
    writing = re.sub("Š", "SZ", writing)
    writing = re.sub("š", "sz", writing)
    writing = re.sub("ĝ", "g", writing)
    writing = re.sub("×", "x", writing)

    # Superscripts become determinatives in {}
    # Subscripts become regular numbers
    # e.g. <sup>d</sup>nin-lil<sub>2</sub> 
    # becomes {d}nin-lil2
    while re.search("<su(p|b)>", writing):
        writing = re.sub( "<sub>([^<]*)</sub>", "\\1", writing )
        writing = re.sub( "<sup>([^<]*)</sup>", "{\\1}", writing )

    # Fix corrupted HTML entities:
    writing = re.sub("Å ", "SZ", writing)
    writing = re.sub("Å¡", "sz", writing)
    writing = re.sub("Ä\x9c", "g", writing)
    writing = re.sub("Ä\x9d", "g", writing)
    writing = re.sub("Ä", "g", writing)
    writing = re.sub("Ã\x97", "x", writing)

    # Some ePSD entries contain ?
    writing = writing.replace("?","")
    return writing

def get_attested_forms( term_id ):
    """
    Find all writings associated with a given word in
    the ePSD. 

    term_id:    string representation of an ePSD id.
                This is found in the URL when browsing
                the dictionary, e.g. it is e1225 in 
                psd.museum.upenn.edu/cgi-bin/xff?xff=e1225
    returns:    a generator yielding the ATF representations
                of writings associated with this word
    """
    with open("epsd/forms/%s"%(term_id)) as term_fp:
        term_soup = BeautifulSoup( term_fp, "html.parser" )
        forms = term_soup.find_all("a", href=True)
        for form in forms:
            if "javascript" not in form["href"]:
                continue
            yield form



###############################################
# Convert scraped ePSD into a serialized 
# python dictionary:

directory = "epsd"
for filename in os.listdir( directory ):
    
    print("Processing file",filename)
    path = os.path.join(directory, filename) 
    if not os.path.isfile( path ):
        continue

    with open( path ) as fp:
        soup = BeautifulSoup( fp, 'html.parser' )

        for term in soup.find_all( "span", class_='summary' ):
            # Cuneiform writings
            writings = term.find_all("span", class_='wr')
            # English equivalents (in short form). E.g. in
            #  bappir [~BEER] "ingredient in beer-making"
            # we extract ~BEER and not "ingredient in beer-
            # making"
            meanings = term.find_all("span", class_='gw')

            # Extract the href element to get
            # this word's term id:
            links = term.find_all("a")
            link = links[0]["href"]
            term_id = link[link.index('\'')+1:-2].replace(".html","")
            # Get additional writings for this term:
            forms = list(get_attested_forms( term_id ))
            # Add additional writings to the list of attested forms:
            writings += forms

            # Use this to get the full English definitions
            # instead of the short-form, single-word definition:
            # meaning = re.search("\"[^\"]*\"", term.text).group(0)[1:-1] 
            # meanings = meaning.split(";")

            for meaning in meanings:
                # Standardise format for definitions:
                # strip whitespace and ~
                meaning = meaning.text
                meaning = meaning.strip()
                meaning = meaning.replace( "~", "" )

                # Try to project a POS tag based on the English
                # definition. This will be very approximate but
                # works as a heuristic until proper POS tagging
                # is implemented for Sumerian
                if meaning != "" and len( meaning.split(" ") ) == 1:
                    # spaCy likes to label words as PROPN in isolation
                    # We add some context to improve accuracy:
                    spacy_sentence = "I saw the word \"%s\"."%(meaning.lower())
                    spacy_tag_ctx = spacy_tagger( spacy_sentence.lower() )[5].tag_[:2]
                    spacy_tag = spacy_tagger(meaning.lower())[0].tag_[:2]

                    _,nltk_tag_ctx = nltk.pos_tag( 
                            ("I saw the word \" %s \" ."%(meaning.lower())).split(" ")
                            )[5][:2]
                    _,nltk_tag = nltk.pos_tag( meaning.lower().split(" ") )[0][:2]

                    # Consensus model: projected tag is None if the
                    # models don't agree
                    tags = [spacy_tag_ctx,spacy_tag,nltk_tag_ctx,nltk_tag]
                    # All models agree:
                    #if all( tags[i] == tags[0] for i in range(len(tags)) ):
                        #consensus = tags[0]
                    # SpaCy models agree that it is a noun:
                    # Downstream task involves identifying nouns
                    # so this is all we bother to annotate for now
                    # Ignore NLTK because SpaCy is usually more accurate
                    if tags.count("NN") >= 2:
                        consensus = "NN"
                    else:
                        consensus = None
                    meaning = ( meaning, consensus )
                else:
                    meaning = ( meaning, None )

                for writing in writings:
                    # For each possible writing of this word,
                    # add it to the dictionary mapped to this
                    # definition:
                    writing = html_to_ascii( writing )
                    dictionary[ writing ].add( meaning )

# Save final dictionary:
np.savez( "epsd.npz", dictionary=dictionary )
