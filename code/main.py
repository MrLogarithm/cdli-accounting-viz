#!flask/bin/python

# TODO every endpoint should have a required argument "corpus"

from flask import Flask, jsonify, request, abort
from flask_swagger_ui import get_swaggerui_blueprint
from flask_caching import Cache

from functools import wraps
import json
import time

from commodify import *
from convert import *
import data

import numpy as np
import scipy.stats
import math

import os
import oyaml
import logging

import itertools


##################################################
# LOGGING

logging.basicConfig(
        filename='commodity-viz-flask.log',
        format='%(asctime)s %(message)s',
        datefmt='%d.%m.%Y %I:%M:%S %p',
        level=logging.INFO
    )

##################################################
# CONFIGURATION

config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        'config.yaml'
    )
with open(config_path, encoding='utf-8') as inp_file:
    config = oyaml.safe_load(inp_file)

##################################################
# CACHING

app = Flask(__name__)
app.config.from_mapping({
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": 3600,
    })
cache = Cache( app )

##################################################
# SWAGGER DOCUMENTATION

SWAGGER_URL = '/docs' 
API_DEF_URL = "http://%s:%s/swagger.json" % (
            config['swagger']['host'],
            config['swagger']['port']
        )

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_DEF_URL,
    config={ 
        'app_name': "CDLI Numeral Conversion"
    },
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

##################################################
# DECORATORS to enforce proper request format
# and allow JSONP GET requests:

def enforce_params( required=[] ):
    """
    Decorator to enforce that a flask endpoint only
    accepts json-formatted queries, and to enforce
    that required parameters are present.

    required    List of required parameter names.
    """
    def argument_decorator( func ):
        @wraps(func) 
        # Need @wraps to ensure flask endpoints stay distinct
        def function_wrapper():
            if request.method == "POST":
                # Enforce JSON request:
                if not request.json:
                    return jsonify({'error': 'Requests must be JSON formatted'}), 400

            # Enforce required parameters:
            for param in required:
                if (request.method == "POST" and param not in request.json) \
                        or (request.method == "GET"  and param not in request.args):
                        return jsonify({'error': 'Missing parameter \'%s\''%(param)}), 400

            # Call wrapped function:
            return func()
        return function_wrapper
    return argument_decorator 

def allow_jsonp(func):
    """
    Decorator to convert POST endpoint to accept
    jsonp GET requests. Adapted from
    https://gist.github.com/aisipos/1094140
    """
    @wraps(func)
    def function_wrapper(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            # Call the wrapped function and edit
            # its response to include the callback
            # function:
            resp, code = func(*args, **kwargs)
            resp.set_data('{}({})'.format(
                str(callback),
                resp.get_data(as_text=True)
            ))
            resp.mimetype = 'application/javascript'
            return resp, code
        else:
            return func(*args, **kwargs)
    return function_wrapper

##################################################
# Method-agnostic accessor for request parameters:

def get_param( key ):
    if request.method == "POST" and key in request.json:
        return request.json[key]
    elif request.method == "GET":
        return request.args.get(key, None)
    return None



##################################################
# API ENDPOINTS

@app.route('/canParse', methods=['POST'])
@enforce_params(required=['query', 'language'])
def canparse_post():
    """
    Return a list of number systems which can 
    parse the query string.
    """
    greedy = False
    if 'greedy' in request.json:
        greedy = request.json['greedy']
    
    if request.json['language'] == "sux":
        results = {system.name:system.canParse( 
            request.json['query'], 
            greedy
        ) for system in convert.convert_sumerian.num_systems}
        response = {"result":[{"system":system,"canparse":results[system]} for system in results]}
    
    
    # To be supported in future release:
    #elif request.json['language'] == "pe":
        #response = convert_susa.convert( request.json['query'] )
    
    else:
        return jsonify({'error': 'Invalid language code: \'%s\''%(request.json['language'])}), 400
    
    return jsonify( response ), 200
    

##################################################


@app.route('/convert', methods=['POST'])
@enforce_params( required=['query', 'language'] )
def convert_post():
    """
    Convert a numeral from ATF to arabic notation.
    """
    if request.json['language'] == "sux":
        try:
            response = {"readings":convert_sumerian.convert( 
                request.json['query'], 
                request.json['system'] if 'system' in request.json else None
            )}
        except:
            return jsonify({'error': 'Failed to convert \'%s\' with language \'%s\' and system \'%s\'. Did you specify the wrong number system?'%( request.json['query'], request.json['language'], request.json['system'] )}), 400


    # To be supported in future release:
    #elif request.json['language'] == "pe":
        #response = convert_susa.convert( request.json['query'] )
    
    else:
        return jsonify({'error': 'Invalid language code: \'%s\''
                        %(request.json['language'])}), 400

    return jsonify( response ), 200


##################################################

def parse_corpus_param():
    corpus = get_param( "corpus" )
    if '+' in corpus:
        return corpus.split("+")
    elif ' ' in corpus:
        return corpus.split(" ")
    elif corpus[0] == 'P':
        return [corpus]
    else:
        # Decode compressed corpus
        encoding_map = {',':'A','0':'B','1':'C','2':'D','3':'E','4':'F','5':'G','6':'H','7':'I','8':'J','9':'K','1,1,':'L','0,':'M','1,':'N','2,':'O','3,':'P','4,':'Q','5,':'R','6,':'S','7,':'T','8,':'U','9,':'V',',0':'W',',1':'X',',2':'Y',',3':'Z',',4':'a',',5':'b',',6':'c',',7':'d',',8':'e',',9':'f','00':'g','11':'h','22':'i','33':'j','44':'k','55':'l','66':'m','77':'n','88':'o','99':'p','0,1':'q','1,1':'r','2,1':'s','3,1':'t','4,1':'u','5,1':'v','6,1':'w','7,1':'x','8,1':'y','9,1':'z',',0,':'0',',1,':'1',',2,':'2',',3,':'3',',4,':'4',',5,':'5',',6,':'6',',7,':'7',',8,':'8',',9,':'9'}
        decoding_map = {v:k for k,v in encoding_map.items()}
        delta_string = ''.join([decoding_map[char] for char in corpus])
        delta_list = list(map(int,delta_string.split(',')))
        ids_list = delta_list[0:1]
        for i in range(1,len(delta_list)):
            ids_list.append( ids_list[-1] + delta_list[i] )
        return ["P%06d"%(id_,) for id_ in ids_list]

def get_dictionary( corpus ):
    all_objects = set()
    pruned_dictionary = {}

    for file_data in get_corpus( corpus ):
        for word in file_data["all_objects"]:
            all_objects.add( word )
            pruned_dictionary[word] = [defn for defn, pos in dictionary[word]]
    return {
        "all_objects": sorted(list(all_objects)),
        "dictionary": pruned_dictionary,
    }


@app.route('/dictionary', methods=['GET', 'POST'])
@allow_jsonp
@enforce_params(["corpus"])
def dictionary_post():
    """
    Returns a list of all the commodities found
    in the specified corpus and a dictionary of
    meanings for those words.
    """
    corpus = parse_corpus_param()
    return jsonify(get_dictionary(corpus)), 200

# TODO refactor to reduce code reuse
# should call commodify module
@app.route('/commodify', methods=['POST','GET'])
@allow_jsonp
@enforce_params(["corpus"])
def commodify_post():
    corpus = parse_corpus_param()

    result = []
    for cdli_no in corpus:
        try:
            result.append( data.commodities.load_data( cdli_no ) )
        except FileNotFoundError:
            commodified_result = commodify_cdli_no( cdli_no )
            result.append( commodified_result )
        except Exception as e:
            pass

    return jsonify( result ), 200


##################################################


@app.route('/getNumberSystems', methods=['POST', 'GET'])
@allow_jsonp
@enforce_params( required=["query", "corpus"] )
def number_systems_post():
    """
    Get a list of all number systems which are 
    used with the query term.
    """
    word = get_param( "query" )
    corpus = parse_corpus_param()

    systems = set()
    for file_data in get_corpus(corpus):
        if word in file_data['values_by_commodity']:
            for readings in file_data['values_by_commodity'][word]:
                for reading in readings:
                    systems.add( reading['system'] )
    return jsonify([{"system":system} for system in systems]), 200


##################################################


@app.route('/summaryStats', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["query","system","corpus"] )
def stats_post():
    """
    Return summary statistics about the counts used
    with a word. 
    """
    def median( lst ):
        """
        Replicating functionality from scipy. scipy is a 
        large dependency and it would be nice to just recreate
        the needed functionality here.
        """
        length = len(lst)
        if length == 0:
            return None
        lst = sorted(lst)
        if length%2 == 0:
            return (lst[(length//2)-1] + lst[length//2]) / 2
        else:
            return lst[length//2]

    word = get_param( "query" )
    system = get_param( "system" )
    corpus = parse_corpus_param()

    readings = all_readings( word, system, corpus )
    units = set(
            reading["unit"] 
            for reading in readings
        )
    if len(units) == 1:
        unit = ' '+list(units)[0]
    else:
        # This should never happen...
        unit = "?"
        print("Too many units attested", units)
    
    values = [ reading["value"]
            for reading in readings
        ]
    summary = scipy.stats.describe(values)
    response = [
        {"statistic":"n-instances", "value":     len(values)},
        {"statistic":"sum", "value":      sum(values)},
        {"statistic":"sum-unit", "value": unit},
        {"statistic":"mean", "value":     summary.mean},
        {"statistic":"variance", "value": summary.variance},
        {"statistic":"stdev", "value":    summary.variance**0.5},
        {"statistic":"skewness", "value": summary.skewness},
        {"statistic":"kurtosis", "value": summary.kurtosis},
        {"statistic":"gmean", "value":  scipy.stats.gmean(values).item()},
        {"statistic":"hmean", "value":  scipy.stats.hmean(values).item()},
        {"statistic":"median", "value": median(values)},
        {"statistic":"mode", "value":   scipy.stats.mode(values).mode.item()},
    ]
    return jsonify(response), 200


##################################################


@app.route('/collocations', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["query", "system", "corpus"] )
def colloc_post():
    """
    Get a list of terms which occur in the same document
    as the query word.
    """
    word = get_param( "query" )
    system = get_param( "system" )
    corpus = parse_corpus_param()

    sources = defaultdict(set)
    def get_other( pair ):
        """
        Given a collocation pair, find the
        word that is *not* the query term.
        """
        if pair[0] == word.replace("_COM",""):
            return pair[1]
        return pair[0]

    pair_counts = defaultdict(int)
    result = []
    for file_data in get_corpus(corpus):
        if word.replace("_COM","") in file_data["all_objects"]:
            for key,readings in file_data['values_by_modified_commodity'].items():
                if word in key.split(" ") and any(r['system'] == system for rr in readings for r in rr):
                    # word appears in this text with the right number system
                    # so we count the pairings:
                    for pair in itertools.combinations(file_data["all_objects"],2):
                        #print(file_data["cdli_no"],pair)
                        if word.replace("_COM", "") in pair:
                            # Sort to avoid spurious distinctions
                            # e.g. (masz, udu) vs (udu, masz)
                            pair = tuple(sorted(pair))
                            pair_counts[pair] += 1
                            sources[get_other(pair)].add( file_data["cdli_no"] )
                    break

    result = [ { 
        "term":get_other(pair),
        "count":count,
        "sources":sorted(list(sources[get_other(pair)]))
    } for pair,count in pair_counts.items() ]

    return jsonify(result), 200


##################################################


@app.route('/collocationsGraph', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["query","system","corpus"] )
def colloc_graph_post():
    """
    Return the same collocation info as /collocations,
    but structured as a graph where edge weights
    equal frequency of term cooccurrence.
    """
    word = get_param( "query" )
    system = get_param( "system" )
    corpus = parse_corpus_param()

    nodes = defaultdict(int)
    links = defaultdict(int)
    occurs_with_query = set()
    for file_data in get_corpus( corpus ):
        for pair in itertools.combinations(file_data['all_objects'],2):
            a, b = sorted(pair)
            nodes[ a ] += 1
            nodes[ b ] += 1
            links[ (a, b) ] += 1
            if word.replace("_COM","") in pair and word in file_data['values_by_commodity'] and any( rr["system"]==system for r in file_data['values_by_commodity'][word] for rr in r ):
                occurs_with_query.add( b )
                occurs_with_query.add( a )

    nodes = [ {
        "id":n,
        "group": 2,
        "defs":list(def_ for def_,pos in dictionary[n] if pos == 'NN')
                if n in dictionary else "",
        "freq":count
        } for n,count in nodes.items()
          if n in occurs_with_query
          and n != word
    ]

    # Shortcut to return if graph is empty:
    if len(nodes) == 0:
        return jsonify({"nodes":[],"links":[]}), 200
    
    links = [ {
        "source":w1["id"],
        "target":w2["id"],
        "count":links[ tuple(sorted([w1["id"], w2["id"]])) ]
        } for i,w1 in enumerate(nodes) for j,w2 in enumerate(nodes) if i!=j ]
    links = [ link for link in links if link['count'] != 0 ]
    # FIXME
    # d3 expects a "value" parameter but this API shouldn't need
    # to know that. Caller should add this parameter themselves.
    for e in links:
        e["value"] = e["count"]

    result = {
                "nodes": nodes,
                "links": links
            } 
    return jsonify(result), 200


##################################################


@app.route('/modifiersGraph', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["query", "system","corpus"] )
def modifier_graph_post():
    """
    Return the same collocation info as /collocations,
    but structured as a graph where edge weights
    equal frequency of term cooccurrence.
    """
    word = get_param( "query" )
    system = get_param( "system" )
    corpus = parse_corpus_param()
    
    nodes = defaultdict(int)
    links = defaultdict(int)
    for file_data in get_corpus( corpus ):
        for key,readings in file_data["values_by_modified_commodity"].items():
            readings_in_chosen_system = [r for r in readings if any(rr["system"]==system for rr in r)]
            if word in key.split(" "):
                modifiers = [re.sub("_[^ ]*", "", mod) for mod in key.split(" ") if "_MOD" in mod]
                for modifier in modifiers:
                    nodes[modifier] += len(readings_in_chosen_system)
                for pair in itertools.combinations(modifiers,2):
                    links[ tuple(sorted(pair)) ] += len(readings_in_chosen_system)

    # Get list of modifiers from the precomputed data:
    nodes = [{
                "id":modifier,
                "group": 2,
                "freq":count,
                "defs":list(def_ for def_,pos in dictionary[modifier] if pos == 'NN')
                      if modifier in dictionary else "",
            }
            for modifier,count in nodes.items()
        ]

    links = [ {
        "source":w1["id"],
        "target":w2["id"],
        "count":links[tuple(sorted([w1["id"],w2["id"]]))],
        } for i,w1 in enumerate(nodes) for j,w2 in enumerate(nodes) if i != j ]
    links = [ link for link in links if link['count'] > 0 ]
    # FIXME
    # d3 expects a "value" parameter but this API shouldn't need
    # to know that. Caller should add this parameter themselves.
    for e in links:
        e["value"] = e["count"]

    result = {
                "nodes": nodes,
                "links": links
            } 
    return jsonify(result), 200


##################################################


@app.route('/modifiers', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["query","system","corpus"] )
def modifiers_post():
    word = get_param( "query" )
    system = get_param( "system" )
    corpus = parse_corpus_param()

    modifier_data=defaultdict(lambda:{"count":0,"sources":set()})
    for file_data in get_corpus(corpus):
        if word.replace("_COM","") in file_data["all_objects"]:
            for key,readings in file_data['values_by_modified_commodity'].items():
                if word in key.split(' ') and any(r['system'] == system for rr in readings for r in rr):
                    #key = re.sub("_[^ ]*", "", key)
                    # How many entries use the specified number system?
                    modifier_data[key]["count"] += len([r for rr in readings for r in rr if r['system']==system])
                    modifier_data[key]["sources"].add(file_data['cdli_no'])
    result = [{
        "modifier": re.sub("_[^ ]*","",key),
        "count": modifier_data[key]["count"],
        "sources": sorted(list(modifier_data[key]["sources"]))
    } for key in modifier_data]
    return jsonify(result), 200


##################################################

def get_corpus( corpus ):
    for cdli_no in corpus:
        try:
            yield data.commodities.load_data( cdli_no )
        except FileNotFoundError:
            try:
                yield commodify_cdli_no( cdli_no )
            except Exception as e:
                pass

def all_readings( word, system, corpus ):
    values = []
    for file_data in get_corpus( corpus ):
        if word in file_data["values_by_commodity"]:
            for readings_list in file_data["values_by_commodity"][word]:
                for reading in readings_list:
                    if reading["system"] == system:
                        values.append( reading )
    return values

@app.route('/allValues', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["query","system","corpus"] )
def values_post():
    """
    Get list of all numeric values associated with the
    query word.
    """
    word   = get_param( "query" )
    system = get_param( "system" )
    corpus = parse_corpus_param()

    readings = all_readings( word, system, corpus )
    values = [{
            "value": reading["value"],
            "unit": reading["unit"]
        } for reading in readings ]
    return jsonify(values), 200


##################################################


@app.route('/concordance', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["query","system","corpus"] )
def concordance_post():
    """
    Return a list of all lines containing some query term.
    """
    word = get_param( "query" )
    system = get_param( "system" )
    corpus = parse_corpus_param()

    unit = ""

    lines = defaultdict(lambda:{"line":None,"sources":set(),"value":None,"count":0})
    for file_data in get_corpus( corpus ):
        for line in file_data["line_data"]:
            line_data = file_data["line_data"][line]
            if word in line_data["counted"]:
                readings = line_data["value"]
                for reading in readings:
                    if reading["system"] == system:
                        lines[line]["sources"].add(file_data["cdli_no"])
                        lines[line]["value"] = reading["value"]
                        lines[line]["count"] += file_data["line_counts"][line]
                        unit = reading["unit"]

    lines = [{
        "line":line,
        "sources":sorted(list(line_data["sources"])),
        "value":("%d %s" if float(line_data["value"]).is_integer() else "%f %s")%(line_data["value"],unit),
        "count":line_data["count"],
        } for line,line_data in lines.items()]
    return jsonify(lines), 200


##################################################


@app.route('/similar', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["query","system","corpus"] )
def similar_post():
    """
    Return a list of words similar to some query word, along
    with a summary of how their distributions differ.
    """
    word = get_param( "query" )
    system = get_param( "system" )
    corpus = parse_corpus_param()

    topk = get_param( "n" )
    if topk is None:
        topk = 5

    distributions = defaultdict(list)
    # Get full distribution for each item:
    for file_data in get_corpus( corpus ):
        for w in file_data["values_by_commodity"]:
            for readings_list in file_data["values_by_commodity"][w]:
                for reading in readings_list:
                    if reading["system"] == system:
                        distributions[w].append(reading['value'])

    n_bins = 10
    range_ = max(distributions[word])
    #range_ = max([max(distributions[w]) for w in distributions])
    # Bin data:
    for w in distributions:
        bins = [0.0 for _ in range(n_bins)]
        for point in distributions[w]:
            idx = int(n_bins*point/range_)
            if idx < len(bins):
              bins[ idx ] += 1
        # offset to eliminate true zeros:
        for b in range(n_bins):
            bins[b] += 1e-10
        Z = sum(bins[b] for b in range(n_bins))
        p = [bins[b] / Z for b in range(n_bins)]
        distributions[w] = p

    def kl_divergence(p, q):
        return sum( [p[i]*math.log( p[i] / q[i] ) for i in range(len(p)) if p[i] != 0], 0 )

    # Get distribution of query word:
    p = distributions[word]

    # Get KL divergence between the query and each other word:
    similarities = []
    for w in distributions:
        q = distributions[w]
        if q == []:
            continue
        divergence = kl_divergence( p, q )
        delta = [q[i]-p[i] for i in range(len(q))]
        similarities.append( (divergence, w, q, delta) )

    result = {"similarities":
        [{
            "divergence":sim,
            "word":re.sub("_[^ ]*", "", w),
            "distribution":[{
                "index":i,
                "value":100*v,
                "label":"%.1f%%"%(100*v),
                "bin":"%d-%d"%(i*range_/n_bins,(i+1)*range_/n_bins),
            } for i,v in enumerate(q)],
            "delta":[{
                "index":i,
                "value":100*v,
                "label":"%+.1f%%"%(100*v),
                "bin":"%d-%d"%(i*range_/n_bins,(i+1)*range_/n_bins),
            } for i,v in enumerate(delta)],
            } for (sim, w, q, delta) in list(sorted(similarities))[1:1+topk]]
    }
    return jsonify(result), 200

##################################################
# Serve JSON from file:

#@app.route('/commodities.json', methods=['GET'])
#@cache.cached(timeout=60*60*24) # Cache timeout of 1 day, 
# because the data doesn't change often
#def coms_get():
    #return jsonify(json_data), 200

@app.route('/swagger.json', methods=['GET'])
def spec_get():
    json_f = open( "swagger.json" )
    json_s = json.load( json_f )
    json_f.close()
    return jsonify( json_s ), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(400)
def malformed(error):
    return jsonify({'error': 'Malformed request.'}), 400

if __name__ == '__main__':
    app.run(
            debug=True, 
            host=config['api']['host'], 
            port=config['api']['port'],
        )
