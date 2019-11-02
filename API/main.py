import argparse
import os
import json
import numpy as np
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from LibNLP import Named

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
        text = json.loads(args['text'])

        # Call NER pipeline


class FindFaceImage(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('image', type=str, location='form')
        super().__init__()

    def post(self):
        args = self.parser.parse_args()
        img_dict = json.loads(args['image'])
        img_array = []
        for name, img in img_dict.items():
            try:
                img = utils.parse_base64.base64_to_image(img)
                img = utils.image_process.preprocess(img)
                img_array.append(img)
            except Exception as e:
                print(e)
                pass

        if len(img_array) == 0:
            abort(500, message='No face was found in the images')
            # response = {'data':None,
            #             'status': 500,
            #             'message': 'No face was found in the images.'}
        else:
            img_array = np.array(img_array).reshape(-1, 160, 160, 3)
            face_probability = one_off_inference(img_array)

            url_template = 'https://www.japanesebeauties.net/japanese/{}/1/{}-1.jpg'

            data = [{'name': k, 'score': str(round(v, 4)), 'url': url_template.format(k, k)} for k, v in
                    face_probability]
            response = {'data': data,
                        'status': 200,
                        'message': 'Success'}
            return response



api.add_resource(FindFaceImage, '/image')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get port numbers')
    parser.add_argument('--port', type=int, required=False, default=8000)

    args = parser.parse_args()
    port = args.port
    #
    app.run(port=port,  debug=False)