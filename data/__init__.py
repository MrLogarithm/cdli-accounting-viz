import re

data_file = open( "data/girsu/transliteration.txt" )
data = data_file.read()
data_file.close()

lined_file = open( "data/girsu/with_lines.txt" )
lined_data = lined_file.read()
lined_file.close()

def clean( text ):
    if isinstance( text, list ):
        text = " ".join(text)
    text = re.sub( "(\$[^$]*\$)", "", text )
    text = re.sub("[*<>\[\]#?!]", "", text )
    text = [ sign.strip() for sign in text.split(" ") if sign.strip() != "" ]
    return text

lined_names = []
lined_texts = []
for line in lined_data.split("\n"):
    if line == "":
        continue
    if line[0] == "&":
        lined_names.append( re.search("P[0-9]{6}", line).group(0) )
        lined_texts.append([])
    else:
        lined_texts[-1].append(clean(line))

def get_by_CDLI_no( cdli_no ):
    index = names.index( cdli_no )
    return texts[ index ]

data = data.split("\n")[:-1]
names = data[0::2]
names = [ re.search( "P[0-9]{6}", name ).group(0) for name in names ]
texts = data[1::2]
texts = [ clean( text ) for text in texts ]
girsu = texts
girsu_lined = lined_texts
