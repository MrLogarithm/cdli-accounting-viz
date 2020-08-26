import json
import segment
import convert
import semantic
import data
import numpy as np
import re
import os
import oyaml
import commodify

from entry import *

from collections import defaultdict

#import mariadb
import MySQLdb as mariadb

##################################################
# CONFIGURATION

config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'config.yaml'
    )
with open(config_path, encoding='utf-8') as inp_file:
    config = oyaml.safe_load(inp_file)

##################################################
# Generates full commodity data for every 
# Sumerian text in the database. 
if __name__ == "__main__":

    # cdli_db langauge ID for Sumerian:
    LANG_ID_SUMERIAN = 5

    conn = mariadb.connect(
            user=config['db']['user'],
            password=config['db']['password'],
            host=config['db']['host'],
            port=config['db']['port'],
            database=config['db']['database']
        )
    cur = conn.cursor()

    # DB query to get all sumerian texts:
    cur.execute("SELECT inscriptions.artifact_id, transliteration FROM inscriptions INNER JOIN artifacts_languages ON inscriptions.artifact_id = artifacts_languages.artifact_id WHERE artifacts_languages.language_id = %s", (LANG_ID_SUMERIAN,))
    cur.fetchall()

    print( "Processing all Sumerian text" )
    print( cur.rowcount, "rows found" )
    i = 1
    for art_no, atf in cur:
        try:
            cdli_no = "P%06d"%(art_no,)
            print( "Done", cdli_no, "\t%d%%"%(100*i / cur.rowcount), end='\r' )
            text = [
                line.strip().split(" ") 
                for line in atf.split("\n")
            ]
            commodify.commodify_text( text, cdli_no )
        except:
            # some texts have errors in the atf
            # no way to recover from this so just fail silently
            pass
        i += 1

    cur.close()
    conn.close()
