#!flask/bin/python
from flask import Flask, jsonify, request, abort, make_response
from commodify import *
import data

app = Flask(__name__)

@app.route('/commodify/api/', methods=['POST'])
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
        # TODO fetch document
        text = data.get_by_CDLI_no( request.json['cdli_no'] )
    elif 'text' in request.json:
        # TODO get text
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
