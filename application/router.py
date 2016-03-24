#!/usr/bin/env python
# coding: utf-8
from flask_restful import reqparse, Resource
from .model import db, Sample
from .utils import genres, mappings
from .lib.custom_model import judge

parser = reqparse.RequestParser()
parser.add_argument('content')
parser.add_argument('type')

class Hello(Resource):
    def get(self):
        return genres.success_response('svm_anti_spam')


class LearnSample(Resource):
    def post(self):
        args = parser.parse_args()
        if args['type'] not in ('negative', 'positive'):
            return genres.fail_response('Type Error')
        if len(args['content']) < 1:
            return genres.fail_response('Content Error')
        types = mappings.TYPE[args['type']]
        db.session.add(Sample(args['content'], types))
        db.session.commit()
        return genres.success_response('ok')


class Judgement(Resource):
    def post(self):
        args = parser.parse_args()
        if len(args['content']) < 1:
            return genres.fail_response('Content Error')
        predict_result = judge(args['content'])
        return genres.success_response({'predict_result': mappings.REV_TYPE[predict_result[0]]})
