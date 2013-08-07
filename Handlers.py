__author__ = 'qitang'

import webapp2
import jinja2
from views import *
import os
import logging
from time import time


#prepare templates
template_dir  = os.path.join(os.path.dirname(__file__),"templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):

    def write(self, *args, **kwargs):
        self.response.write(*args, **kwargs)

    def render_str(self, template, **kwargs):
        t = jinja_env.get_template(template)
        return t.render(kwargs)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))


class MainHandler(Handler):
    def get(self):
        self.render("index.html")


class StoryHandler(Handler):
    def get(self):
        startTime = time()
        articles = retrieveLatest(dictByLabel["storyUrlDict"])
        elapseTime = (time()-startTime)*1000
        logging.info(elapseTime)
        errorMsg = "this is the error msg"
        self.render("story.html", articles=articles, errorMsg=errorMsg)

class TravelHandler(Handler):
    def get(self):
        articles = retrieveLatest(dictByLabel["travelUrlDict"])
        errorMsg = "this is the news error message"
        self.render("travel.html", articles=articles, errorMsg=errorMsg)

class OpinionHandler(Handler):
    def get(self):
        articles = retrieveLatest(dictByLabel["opinionUrlDict"])
        errorMsg = "this is the news error message"
        self.render("opinion.html", articles=articles, errorMsg=errorMsg)

class ManHandler(Handler):
    def get(self):
        articles = retrieveLatest(dictByLabel["manUrlDict"])
        errorMsg = "this is the news error message"
        self.render("man.html", articles=articles, errorMsg=errorMsg)

class WomanHandler(Handler):
    def get(self):
        articles = retrieveLatest(dictByLabel["womanUrlDict"])
        errorMsg = "this is the news error message"
        self.render("woman.html", articles=articles, errorMsg=errorMsg)

class LifeHandler(Handler):
    def get(self):
        articles = retrieveLatest(dictByLabel["lifeUrlDict"])
        errorMsg = "this is the news error message"
        self.render("life.html", articles=articles, errorMsg=errorMsg)

class TechnologyHandler(Handler):
    def get(self):
        articles = retrieveLatest(dictByLabel["technologyUrlDict"])
        errorMsg = "this is the news error message"
        self.render("technology.html", articles=articles, errorMsg=errorMsg)


class BooksHandler(Handler):
    def get(self):
        articles = retrieveLatest(dictByLabel["booksUrlDict"])
        errorMsg = "this is the news error message"
        self.render("books.html", articles=articles, errorMsg=errorMsg)


class ArtHandler(Handler):
    def get(self):
        articles = retrieveLatest(dictByLabel["artUrlDict"])
        errorMsg = "this is the news error message"
        self.render("art.html", articles=articles, errorMsg=errorMsg)


class SuperAdmin(Handler):
    def get(self):
        logging.info("Initializing the data processing")
        runApplication()


