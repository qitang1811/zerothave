__author__ = 'qitang'

from google.appengine.ext import db


class Article(db.Model):
    title = db.StringProperty(indexed=False)
    description = db.TextProperty(indexed=False)
    imgLink = db.StringProperty(indexed=False)
    link = db.StringProperty(indexed=False)
    srcName = db.StringProperty(indexed=True)
    labelName = db.StringProperty(indexed=True)

