import re

data_file = open( "data/girsu/transliteration.txt" )
data = data_file.read()
data_file.close()

data = data.split("\n")[:-1]
names = data[0::2]
names = [ re.search( "P[0-9]{6}", name ).group(0) for name in names ]
texts = data[1::2]
texts = [ re.sub( "[*<>\[\]#?!]", "", text ) for text in texts ]
texts = [ [ sign.strip() for sign in text.split(" ") if sign.strip() != "" ] for text in texts ]
girsu = texts
