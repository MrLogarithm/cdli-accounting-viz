#!flask/bin/python
from flask import Flask, jsonify, request, abort, make_response
from flask_swagger_ui import get_swaggerui_blueprint
from flask_caching import Cache
from commodify import *
from convert import *
import data
import json
import numpy as np
import scipy.stats
from functools import wraps
import time

config = {
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": 3600,
    }

app = Flask(__name__)
app.config.from_mapping( config )
cache = Cache( app )

##################################################
# SWAGGER DOCUMENTATION

SWAGGER_URL = '/docs' 
API_URL = 'https://cdli-numerals.herokuapp.com/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={ 
        'app_name': "CDLI Numeral Conversion"
    },
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

##################################################
# Re-load static data:

json_data = dict()
last_data_load = None
DATA_TIMEOUT = 360
def load_static_data():
    print("Loading static data...")
    global json_data
    json_f = open( "commodities.json" )
    json_data = json.load( json_f )
    last_data_load = time.time()
    json_f.close()

##################################################
# Decorator to enforce proper request format:

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
                # Enforce JSON formatted parameters:
                if not request.json:
                    return make_response(
                        jsonify({'error': 'Requests must be JSON formatted'}), 
                        400)

            # Enforce required parameters:
            for param in required:
                if (request.method == "POST" and param not in request.json) \
                        or (request.method == "GET"  and param not in request.args):
                        return make_response(
                            jsonify({'error': 'Missing parameter \'%s\''%(param)}), 
                            400)

            # Reload static data dump if it's out of date:
            if last_data_load is None or time.time()-last_data_load > DATA_TIMEOUT:
                load_static_data()

            # Call wrapped function:
            return func()
        return function_wrapper
    return argument_decorator 

def allow_jsonp(func):
    """
    Decorator to convert flask endpoint to accept
    jsonp GET requests. Adapted from
    https://gist.github.com/aisipos/1094140
    """
    @wraps(func)
    def function_wrapper(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            resp, code = func(*args, **kwargs)
            print(resp)
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
#

def get_param( key ):
    if request.method == "POST":
        return request.json[key]
    elif request.method == "GET":
        return request.args.get(key, None)

##################################################
# API endpoints:

@app.route('/canparse', methods=['POST'])
@enforce_params(required=['query', 'language'])
def canparse_post():
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
        return make_response(
                jsonify({'error': 'Invalid language code: \'%s\''
                        %(request.json['language'])}
                    ), 400)
    
    return jsonify( response ), 200
    
@app.route('/convert', methods=['POST'])
@enforce_params( required=['query', 'language'] )
def convert_post():
    if request.json['language'] == "sux":
        try:
            response = {"readings":convert_sumerian.convert( 
                request.json['query'], 
                request.json['system'] if 'system' in request.json else None
            )}
        except:
            return make_response(
                jsonify({'error': 'Failed to convert \'%s\' with language \'%s\' and system \'%s\'. Did you specify the wrong number system?'%( request.json['query'], request.json['language'], request.json['system'] )}), 
                400)


    # To be supported in future release:
    #elif request.json['language'] == "pe":
        #response = convert_susa.convert( request.json['query'] )
    
    else:
        return make_response(
                jsonify({'error': 'Invalid language code: \'%s\''
                        %(request.json['language'])}
                    ), 400)

    return jsonify( response ), 200

@app.route('/commodify', methods=['POST'])
@enforce_params()
def commodify_post():
    text = None
    if 'cdli_no' in request.json:
        if 'text' in request.json:
            return make_response(
                jsonify({'error': 'Please specify \'cdli_no\' or \'text\', not both.'}), 
                400)
        text = ' '.join( data.get_by_CDLI_no( request.json['cdli_no'] ) )
    elif 'text' in request.json:
        text = data.clean( request.json['text'] )
        text = ' '.join(text)
    else:
        return make_response(
            jsonify({'error': 'Missing parameter \'cdli_no\' or \'text\'.'}), 
            400)
    #print(text)

    # convert to tuple so that objects are serializable:
    response = commodify( text )
    response = {"entries": [
        {field:entry.__getattribute__(field) for field in entry.__fields__} for entry in response
        ]}
    return jsonify( response ), 200

@app.route('/getNumberSystems', methods=['POST', 'GET'])
@allow_jsonp
@enforce_params( required=["word"] )
def number_systems_post():
    word = get_param( "word" )
    systems = set(
            reading['system'] 
            for readings_list in json_data['values_by_commodity'][word] 
            for reading in readings_list
        )
    return jsonify(list(sorted(systems))), 200

@app.route('/summaryStats', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["word","system"] )
def stats_post():
    word = get_param( "word" )
    system = get_param( "system" )

    readings = json_data['values_by_commodity'][word]

    units = set(
            reading["unit"] 
            for readings_list in readings 
            for reading in readings_list 
            if reading["system"] == system
        )
    if len(units) == 1:
        unit = ' '+list(units)[0]
    else:
        unit = "?"
        print("Too manty units attested!", units)
    
    values = [ reading["value"]
            for readings_list in readings 
            for reading in readings_list 
            if reading["system"] == system
        ]
    summary = scipy.stats.describe(values)
    response = [
        {"n-instances":     len(values)},
        {"sum":      sum(values)},
        {"sum-unit": unit},
        {"mean":     summary.mean},
        {"variance": summary.variance},
        {"stdev":    summary.variance**0.5},
        {"skewness": summary.skewness},
        {"kurtosis": summary.kurtosis},
        {"gmean":  scipy.stats.gmean(values).item()},
        {"hmean":  scipy.stats.hmean(values).item()},
        {"median": np.median(values)},
        {"mode":   scipy.stats.mode(values).mode.item()},
    ]
    return jsonify(response), 200

@app.route('/collocations', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["word"] )
def colloc_post():
    word = get_param( "word" )
    word = re.sub("_[^ ]*", "", word)

    collocations = json_data["collocation_counts"]
    collocations = { 
            colloc:count 
            for colloc,count in collocations.items() 
            if word in colloc.split(" ")
        }
    def get_other( colloc ):
        colloc = colloc.split(" ")
        if colloc[0] == word:
            return colloc[1]
        return colloc[0]
    result = [ {
                "term":get_other( colloc ),
                "count":count
            } 
            for colloc, count in collocations.items()
        ]
    return jsonify(result), 200

@app.route('/modifiersGraph', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["word"] )
def modifier_graph_post():
    word = get_param( "word" )
    word = re.sub("_[^ ]*", "", word)

    nodes = [{
                "id":modifier,
                "group": 1,
                "freq":len(readings),
                "def":sorted(list(dictionary[modifier]))[0][0] 
                      if modifier in dictionary else "",
            }
            for key,readings in json_data['values_by_modified_commodity'].items()
            for modifier in re.sub("_[^ ]*", "", key).split(" ")
            if word in key
            #and any(r['system'] == system for rr in readings for r in rr)
        ]
    unique_nodes = []
    for node in nodes:
        if node['id'] == word or any(n["id"] == node["id"] for n in unique_nodes):
            continue
        unique_nodes.append(node)
    nodes = unique_nodes
    """
    nodes = list(set(sum([[w1,w2] for w1,w2 in collocation_lists],[])))
    nodes = [ {
        "id":n,
        "group":1 if n==word else 2,
        "def":sorted(list(dictionary[n]))[0][0] if n in dictionary else "",
        "freq":collocations["%s %s"%(n,word)] 
            if "%s %s"%(n,word) in collocations 
            else collocations["%s %s"%(word,n)]
            if "%s %s"%(word,n) in collocations 
            else 0
        } for n in nodes ]
    if len(nodes) == 0:
        return jsonify({"nodes":[],"links":[]}), 200
    """
    def getCombinedModCount( base, mod1, mod2 ):
        total = 0
        mod1 = mod1["id"] + "_MOD"
        mod2 = mod2["id"] + "_MOD"
        for key, counts in json_data['values_by_modified_commodity'].items():
            if base in key and mod1 in key and mod2 in key:
                # TODO limit to one number system, here and in other graph code
                system = 'cardinal'
                for count_list in counts:
                    for count in count_list:
                        if count['system'] == system:
                            total += count['value']
                            break
        return total
    edges = [ {
        "source":w1["id"],
        "target":w2["id"],
        "count":getCombinedModCount(word,w1,w2),
        #collocations["%s %s"%(w1["id"],w2["id"])] 
            #if "%s %s"%(w1["id"],w2["id"]) in collocations 
            #else collocations["%s %s"%(w2["id"],w1["id"])]
            #if "%s %s"%(w2["id"],w1["id"]) in collocations 
            #else 0
        } for w1 in nodes for w2 in nodes ]
    for e in edges:
        e["value"] = e["count"]
    result = {
                "nodes": nodes,
                "links": edges
            } 
    return jsonify(result), 200

@app.route('/collocationsGraph', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["word"] )
def colloc_graph_post():
    word = get_param( "word" )
    word = re.sub("_[^ ]*", "", word)

    def get_other( colloc ):
        #colloc = colloc.split(" ")
        if colloc[0] == word:
            return colloc[1]
        return colloc[0]

    collocations = json_data["collocation_counts"]

    collocation_lists = defaultdict(dict)
    c = { 
        tuple(sorted(colloc.split(" "))):count
        for colloc,count in collocations.items() 
        if word in colloc.split(" ")
    }
    collocation_lists.update(c)

    distance = 1
    for d in range(2,distance+1):
        # Get words in outer ring of the graph:
        source_words = set(sum([[u,v] for u,v in collocation_lists],[]))
        for w in source_words:
            c = { 
                tuple(sorted(colloc.split(" "))):count
                for colloc,count in collocations.items() 
                if w in colloc.split(" ")
            }
            collocation_lists.update(c)

    nodes = list(set(sum([[w1,w2] for w1,w2 in collocation_lists],[])))
    nodes = [ {
        "id":n,
        "group":1 if n==word else 2,
        "def":sorted(list(dictionary[n]))[0][0] if n in dictionary else "",
        "freq":collocations["%s %s"%(n,word)] 
            if "%s %s"%(n,word) in collocations 
            else collocations["%s %s"%(word,n)]
            if "%s %s"%(word,n) in collocations 
            else 0
        } for n in nodes 
        if n != word
        ]
    if len(nodes) == 0:
        return jsonify({"nodes":[],"links":[]}), 200
    edges = [ {
        "source":w1["id"],
        "target":w2["id"],
        "count":collocations["%s %s"%(w1["id"],w2["id"])] 
            if "%s %s"%(w1["id"],w2["id"]) in collocations 
            else collocations["%s %s"%(w2["id"],w1["id"])]
            if "%s %s"%(w2["id"],w1["id"]) in collocations 
            else 0
        } for w1 in nodes for w2 in nodes ]
    for e in edges:
        e["value"] = e["count"]
    result = {
                "nodes": nodes,
                "links": edges
            } 
    return jsonify(result), 200

@app.route('/allValues', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["word","system"] )
def values_post():
    word = get_param( "word" )
    system = get_param( "system" )

    readings = json_data['values_by_commodity'][word]
    values = [ {"value":reading["value"]}
            for readings_list in readings 
            for reading in readings_list 
            if reading["system"] == system
        ]
    return jsonify(values), 200

@app.route('/concordance', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["word","system"] )
def concordance_post():
    word = get_param( "word" )
    system = get_param( "system" )
    lines = [
            {"line":line, "value":json_data["line_data"][line]["value"], "count":count} 
            for line,count in json_data["line_counts"].items()
            if word in json_data["line_data"][line]["counted"]
        ]
    return jsonify(lines), 200

@app.route('/modifiers', methods=['POST','GET'])
@allow_jsonp
@enforce_params( required=["word","system"] )
def modifiers_post():
    word = get_param( "word" )
    system = get_param( "system" )
    result = [{
                "modifier":re.sub("_[^ ]*", "", key),
                "count":len(readings)
            }
            for key,readings in json_data['values_by_modified_commodity'].items()
            if word in key
            and any(r['system'] == system for rr in readings for r in rr)
            ]
    return jsonify(result), 200


##################################################
# Serve JSON from file:

@app.route('/commodities.json', methods=['GET'])
@cache.cached(timeout=60*60*24) # Cache timeout of 1 day, 
# because the data doesn't change often
def coms_get():
    return make_response( json_data, 200 )

@app.route('/swagger.json', methods=['GET'])
def spec_get():
    json_f = open( "swagger.json" )
    json_s = json.load( json_f )
    json_f.close()
    return make_response( json_s, 200 )

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Malformed request.'}), 400)

if __name__ == '__main__':
    app.run(debug=True)
