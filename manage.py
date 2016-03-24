#!/usr/bin/env python
# coding: utf-8
import sys
from os import path
from flask import Flask
from flask_restful import Api

from application import router
from application.model import db, Sample

app = Flask(__name__)
database_path = path.join('sqlite:///', path.dirname(__file__), 'sample.db')

app.config.setdefault('SQLALCHEMY_DATABASE_URI', database_path)
app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)

db.init_app(app)

api = Api(app)
api.add_resource(router.Hello, '/')
api.add_resource(router.LearnSample, '/sample/')
api.add_resource(router.Judgement, '/judge/')

if __name__ == '__main__':
    try:
        action = sys.argv[1]
    except IndexError:
        print('action:\n\trun - start http service\n\tinitdb - init sqlite schema')
        exit(0)
    if action == 'run':
        from application.lib.custom_model import learn_sample
        print('start learning...')
        with app.app_context():
            learn_sample()
        print('learning succeed')
        app.run(debug=True)
    elif action == 'initdb':
        from application.utils import mappings
        print('start init db...')
        count = [0, 0]
        with app.app_context():
            db.create_all()
            with open('./application/lib/positive.txt') as f:
                for row in f.readlines():
                    if len(row) > 0:
                        count[1] += 1
                        db.session.add(Sample(row, mappings.TYPE['positive']))
            with open('./application/lib/negative.txt') as f:
                for row in f.readlines():
                    if len(row) > 0:
                        count[0] += 1
                        db.session.add(Sample(row, mappings.TYPE['negative']))
            db.session.commit()
        print('insert samples: negative %d, positive %d' % tuple(count))
        print('done...')
    elif action == 'testmodle':
        from application.lib import custom_model
        from sklearn.metrics import f1_score
        import random
        custom_model.learn_sample(from_file=True)
        sentences = custom_model.read_data_from_file()
        random.shuffle(sentences)
        test_set = sentences[:100]
        # seprate data_set
        test_value, test_result = custom_model.seprate_value_result(test_set)
        predicted_result = custom_model.judge(test_value)
        print('Predicted Result: \n', predicted_result)
        print('Correct Result: \n', test_result)

        # score
        test_size = len(test_value)
        score = 0
        for i in range(test_size):
            if predicted_result[i] == test_result[i]:
                score += 1
        print('Got %s out of %s' %(score, test_size))
        f1 = f1_score(test_result, predicted_result, average='binary')
        print('f1 = %.2f' %(f1))

