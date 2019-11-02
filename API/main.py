import argparse
import os
import json
import numpy as np
import nlp_lib
import multiprocessing as mp
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from functools import partial

THIS_DIR = os.path.dirname(__file__)

app = Flask(__name__)
app.debug = False
api = Api(app)

class TextAnalytics(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('text', type=str, location='form')
        super().__init__()

    def post(self):
        args = self.parser.parse_args()
        print(args)
        text = args['text']

        try:
            # Call NER pipeline
            entities = nlp_lib.NER.extract_interesting_entities(text)

            # q = mp.Queue()

            jobs = [nlp_lib.google_news_query, nlp_lib.hkex_query, nlp_lib.law_suits_data,
                    nlp_lib.stock_data, nlp_lib.twitter_data]
            names = ['GoogleNews', 'TabularData', 'HKEX', 'LawSuits', 'StockData', 'Twitter']
            results = {}

            results['GoogleNews'] = nlp_lib.google_news_query(entities)
            results['StockData'] = nlp_lib.stock_data(text)

            # package response
            response = {
                'entites': entities,
                'suggestions': results,
                'status code': 200,
                'message': 'success'
            }
            return response
        except Exception as e:
            abort(500, message=e)

class SummaryAnalytics(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('text', type=str, location='form')
        super().__init__()

    def post(self):
        args = self.parser.parse_args()
        print(args)
        text = args['text']

        try:
            results = {}
            results['TabularData'] = nlp_lib.tabular_extracion(nlp_lib.NLP(text), text)

            # package response
            response = {
                'suggestions': results,
                'status code': 200,
                'message': 'success'
            }
            return response
        except Exception as e:
            abort(500, message=e)



api.add_resource(TextAnalytics, '/text')
api.add_resource(SummaryAnalytics, '/adhocSummary')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get port numbers')
    parser.add_argument('--port', type=int, required=False, default=8000)

    args = parser.parse_args()
    port = args.port
    #
    app.run(port=port, host='0.0.0.0', debug=False)