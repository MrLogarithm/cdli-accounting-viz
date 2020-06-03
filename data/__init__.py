import re

data_file = open( "data/girsu/transliteration.txt" )
data = data_file.read()
data_file.close()

def get_by_CDLI_no( cdli_no ):
    index = names.index( cdli_no )
    return texts[ index ]

def clean( text ):
    if isinstance( text, list ):
        text = " ".join(text)
    text = re.sub("[*<>\[\]#?!]", "", text )
    text = [ sign.strip() for sign in text.split(" ") if sign.strip() != "" ]
    return text

data = data.split("\n")[:-1]
names = data[0::2]
names = [ re.search( "P[0-9]{6}", name ).group(0) for name in names ]
texts = data[1::2]
texts = [ clean( text ) for text in texts ]
girsu = texts

