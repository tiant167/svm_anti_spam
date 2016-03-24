#!/usr/bin/env python
# coding: utf-8

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    type = db.Column(db.Integer)

    def __init__(self, content, type):
        self.content = content
        self.type = type

    def __repr__(self):
        return '<Sample %r...>' % self.content[0:10]
