import json
import os
import gzip

def load_data( cdli_no ):
    file_path = os.path.join("data", "commodities", "{0}.json.gz".format(cdli_no))
    with gzip.open( file_path, 'rb' ) as fp:
        return json.loads( fp.read() )
