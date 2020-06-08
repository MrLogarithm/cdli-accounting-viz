#!flask/bin/python
from flask import Flask, jsonify, request, abort, make_response
from commodify import *
from convert import *
import data

app = Flask(__name__)

@app.route('/canparse', methods=['POST'])
def canparse_post():
    if not request.json:
        return make_response(
                jsonify({'error': 'Requests must be JSON formatted'}), 
                400)

    if not 'query' in request.json:
        return make_response(
                jsonify({'error': 'Missing parameter \'query\''}), 
                400)
    if not 'language' in request.json:
        return make_response(
                jsonify({'error': 'Missing parameter \'language\''}), 
                400)

    greedy = False
    if 'greedy' in request.json:
        greedy = request.json['greedy']

    if request.json['language'] == "sux":
        response = {system.name:system.canParse( 
            request.json['query'], 
            greedy
        ) for system in convert.convert_sumerian.num_systems}


    # To be supported in future release:
    #elif request.json['language'] == "pe":
        #response = convert_susa.convert( request.json['query'] )
    
    else:
        return make_response(
                jsonify({'error': 'Invalid language code: \'%s\''
                        %(request.json['language'])}
                    ), 400)

    return jsonify( response ), 201
        
@app.route('/convert', methods=['POST'])
def convert_post():
    if not request.json:
        return make_response(
                jsonify({'error': 'Requests must be JSON formatted'}), 
                400)

    if not 'query' in request.json:
        return make_response(
                jsonify({'error': 'Missing parameter \'query\''}), 
                400)
    if not 'language' in request.json:
        return make_response(
                jsonify({'error': 'Missing parameter \'language\''}), 
                400)


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

    return jsonify( response ), 201

@app.route('/commodify', methods=['POST'])
def commodify_post():
    if not request.json:
        return make_response(
                jsonify({'error': 'Requests must be JSON formatted'}), 
                400)

    text = None
    if 'cdli_no' in request.json:
        if 'text' in request.json:
            return make_response(
                jsonify({'error': 'Please specify \'cdli_no\' or \'text\', not both.'}), 
                400)
        text = data.get_by_CDLI_no( request.json['cdli_no'] )
    elif 'text' in request.json:
        text = data.clean( request.json['text'] )
    else:
        return make_response(
            jsonify({'error': 'Missing parameter \'cdli_no\' or \'text\'.'}), 
            400)

    # convert to tuple so that objects are serializable:
    response = commodify( text )
    response = {"entries": [
        {field:entry.__getattribute__(field) for field in entry.__fields__} for entry in response
        ]}
    return jsonify( response ), 201

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Malformed request.'}), 400)

if __name__ == '__main__':
    app.run(debug=True)
