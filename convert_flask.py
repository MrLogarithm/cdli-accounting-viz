#!flask/bin/python
from flask import Flask, jsonify, request, abort, make_response
from convert import *

app = Flask(__name__)

@app.route('/numerals/api/convert', methods=['POST'])
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

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Malformed request.'}), 400)

if __name__ == '__main__':
    app.run(debug=True)
