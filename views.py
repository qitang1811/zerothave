__author__ = 'qitang'


#import fix_path
import jinja2
from google.appengine.ext import db
from urllib2 import HTTPError, URLError
from lib.bs4 import BeautifulSoup
from lib.feedparser import parse
from models import Article
from random import shuffle
import logging
from datetime import datetime
from time import strptime, sleep
from models import Article

#used for retrieving data and render to web page
dictByLabel = {
                "travelUrlDict": {"newYorkTimes_travel": "http://rss.nytimes.com/services/xml/rss/nyt/Travel.xml",},

                "storyUrlDict": {"newYorker_story": "http://www.newyorker.com/services/mrss/feeds/reporting.xml",
                                "newYorkTimes_story": "http://rss.nytimes.com/services/xml/rss/nyt/GlobalHome.xml",
                                "time_story" : "http://feeds2.feedburner.com/time/topstories",
                                "reddit_story": "http://www.reddit.com/.rss",},
               "opinionUrlDict": {"washingtonPost_opinion": "http://feeds.washingtonpost.com/rss/opinions",
                                  "time_opinion": "http://feeds.feedburner.com/time/ideas",
                                  "wsj_opinion": "http://online.wsj.com/xml/rss/3_7041.xml",
                                  "newYorker_opinion": "http://www.newyorker.com/services/mrss/feeds/comment.xml"},
               "manUrlDict": {"fhm_man": "http://rss.feedsportal.com/c/375/f/434908/index.rss",
                              "gq_man": "http://www.gq.com/services/rss/feeds/women.xml",},

               "artUrlDict": {"bbc_art": "http://feeds.bbci.co.uk/news/video_and_audio/entertainment_and_arts/rss.xml",
                              "newYorker_art": "http://www.newyorker.com/services/mrss/feeds/arts.xml",
                              "newYorkTimes_art": "http://rss.nytimes.com/services/xml/rss/nyt/Arts.xml",},
               "womanUrlDict":{"entertainment_woman": "http://syndication.eonline.com/syndication/feeds/rssfeeds/celebrityphotos.xml",
                               "fhm_woman": "http://feeds.eonline.com/eonline/fashion",
                               "people_woman": "http://feeds.feedburner.com/people/photos",},
               "booksUrlDict": {"newYorker_books": "http://www.newyorker.com/services/mrss/feeds/fiction.xml",
                                "newYorkTimes_books": "http://rss.nytimes.com/services/xml/rss/nyt/Books.xml"},
               "lifeUrlDict": {"washingtonPost_life": "http://feeds.washingtonpost.com/rss/lifestyle",
                               "time_life" : "http://feeds.feedburner.com/time_life",
                               "bbc_life": "http://feeds.bbci.co.uk/news/in_pictures/rss.xml",},
               "technologyUrlDict" :{"time_technology": "http://feeds.feedburner.com/timeblogs/nerd_world",
                                     "bbc_technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",
                                     "newYorkTimes_technology": "http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
                                     "wired_technology": "http://feeds.wired.com/wired/index",}
               }
#used for parsing xml and store data
dictBySrc = {
        "washingtonPost":{"washingtonPost_life": "http://feeds.washingtonpost.com/rss/lifestyle",
                          "washingtonPost_opinion": "http://feeds.washingtonpost.com/rss/opinions",
                          },
        "time":{"time_story": "http://feeds2.feedburner.com/time/topstories",
                "time_life": "http://feeds.feedburner.com/time_life",
                "time_opinion": "http://feeds.feedburner.com/time/ideas",
                "time_technology": "http://feeds.feedburner.com/timeblogs/nerd_world",

                },
        "fhm": {"fhm_man": "http://rss.feedsportal.com/c/375/f/434908/index.rss",
                "fhm_woman": "http://feeds.eonline.com/eonline/fashion",
               },
        "bbc":{ "bbc_life": "http://feeds.bbci.co.uk/news/in_pictures/rss.xml",
                "bbc_technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",
                "bbc_art": "http://feeds.bbci.co.uk/news/video_and_audio/entertainment_and_arts/rss.xml",},
        "gq":{"gq_man": "http://www.gq.com/services/rss/feeds/women.xml",},
        "wsj":{"wsj_opinion": "http://online.wsj.com/xml/rss/3_7041.xml",},
        "entertainment" :{"entertainment_woman": "http://syndication.eonline.com/syndication/feeds/rssfeeds/celebrityphotos.xml",},
        "people": {"people_woman": "http://feeds.feedburner.com/people/photos"},
        "forbes": {"forbes_technology": "http://www.forbes.com/technology/feed/",},
        "reddit": {"reddit_story": "http://www.reddit.com/.rss",},
        "newYorker":{"newYorker_story": "http://www.newyorker.com/services/mrss/feeds/reporting.xml",
                     "newYorker_art": "http://www.newyorker.com/services/mrss/feeds/arts.xml",
                     "newYorker_opinion": "http://www.newyorker.com/services/mrss/feeds/comment.xml",
                     "newYorker_books": "http://www.newyorker.com/services/mrss/feeds/fiction.xml",},
        "newYorkTimes": {"newYorkTimes_story": "http://rss.nytimes.com/services/xml/rss/nyt/GlobalHome.xml",
                         "newYorkTimes_art": "http://rss.nytimes.com/services/xml/rss/nyt/Arts.xml",
                         "newYorkTimes_books": "http://rss.nytimes.com/services/xml/rss/nyt/Books.xml",
                         "newYorkTimes_travel": "http://rss.nytimes.com/services/xml/rss/nyt/Travel.xml",
                         "newYorkTimes_technology": "http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"},
        "wired": {"wired_technology": "http://feeds.wired.com/wired/index",}

}


class BaseParser:
    def __init__(self, url=None, last_published=None, doc=None, srcName=None):
        self.url = url
        self.last_published = last_published
        self.doc = doc
        self.srcName = srcName

    def retrieveDoc(self):
        try:
            doc = parse(self.url)
        except HTTPError, e:
            raise e.message
        except URLError, e:
            raise e.message
        self.doc = doc


    def checkUpdated(self):
        #parse the xml first
        self.retrieveDoc()
        try:
            current_time = self.doc.feed.updated_parsed
        except AttributeError as e:
            current_time = buildCurrentTime()
        if self.last_published is None or current_time > self.last_published:
            self.parseAndStoreDoc()
            self.last_published = current_time
            #if we have updated article, clean
            CACHE[self.srcName].clear()

    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            soup = BeautifulSoup(e.description)
            description = jinja2.Markup(soup.getText()).unescape()
            #truncate the length of
            if len(description) > 500:
                description = description[:500]

            link = e.links[0]["href"]
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            # if no image in entry, use the source logo instead
            try:
                imgLink = e.media_content[0]["url"]
            except AttributeError as e:
                imgLink = self.doc.feed.image["href"]
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data to database!(from %s)" %srcName)


#useless class
class WashingtonPost(BaseParser):
    '''
    no image in this entry, use the washtingtonPost logo instead

    '''
    logoSrc = "/static/img/logos/The-Washington-Post-logo.gif"
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            desc = BeautifulSoup(e.description).findAll("p")[0].getText()
            description = jinja2.Markup(desc).unescape()
            #truncate the length
            if len(description) > 500:
                description = description[:500]
            link = e.links[0]["href"]
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            #img from feed
            imgLink = WashingtonPost.logoSrc
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("storing data from %s" %srcName)

class FHM(BaseParser):
    '''
    feed for man
    '''
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            link = e.links[0]["href"]
            soup = BeautifulSoup(e.description)
            description = jinja2.Markup(soup.getText()).unescape()
            imgLink = soup.findAll("img")[0].get("src")
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data from %s" %srcName)


class BBC(BaseParser):
    """
    feed from bbc
    """
    bbcLogo = "/static/img/logos/bbcLogo.gif"
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            link = e.links[0]["href"]
            description = e.description
            #retrieve the img link if not exit use logo instead
            try:
                imgLink = e.media_thumbnail[0]["url"]
            except AttributeError as e:
                imgLink = BBC.bbcLogo
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data from %s" %srcName)

class GQ(BaseParser):
    """
    FEED FROM GQ
    """
    gqLogo = '/static/img/logos/gqLogo.gif'
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            link = e.links[0]["href"]
            soup = BeautifulSoup(e.description)
            try:
                description = jinja2.Markup(soup.findAll("p")[-1]).unescape()
            except IndexError as e:
                description = jinja2.Markup(soup).unescape()

            # try:
            #     imgLink = soup.findAll("img")[0]["src"]
            # except IndexError as e:
            imgLink = GQ.gqLogo

            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data from %s" %srcName)

class WSJ(BaseParser):
    """
    feed from wall street journal
    """
    wsjLogo = '/static/img/logos/wsjLogo.gif'
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            description = jinja2.Markup(e.description).unescape()
            link = e.links[0]["href"]
            imgLink = WSJ.wsjLogo
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data from %s" %srcName)


class Entertainment(BaseParser):
    """
    feed from entertainment e online
    """
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            link = e.link
            imgLink = e.imgurl
            soup = BeautifulSoup(e.description)
            description = jinja2.Markup(soup.getText()).unescape()
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data from %s" %srcName)


class People(BaseParser):
    """
    feed from bbc
    """
    bbcLogo = "/static/img/logos/bbcLogo.gif"
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            link = e.links[0]["href"]
            soup = BeautifulSoup(e.description)
            description = jinja2.Markup(soup.getText()).unescape()
            #retrieve the img link if not exit use logo instead
            try:
                imgLink = e.media_thumbnail[0]["url"]
            except AttributeError as e:
                imgLink = BBC.bbcLogo
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data from %s" %srcName)

class Reddit(BaseParser):
    """
    no description
    """
    redditLogo = "/static/img/logos/redditLogo.gif"
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            link = e.links[0]["href"]
            description = ""
            #retrieve the img link if not exit use logo instead
            try:
                imgLink = e.media_thumbnail[0]["url"]
            except AttributeError as e:
                imgLink = Reddit.redditLogo
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data from %s" %srcName)


class NewYorker(BaseParser):
    """
    feed from new york
    """
    logo = "/static/img/logos/newYorkerLogo.gif"
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            soup = BeautifulSoup(e.description)
            description = jinja2.Markup(soup.getText()).unescape()
            #truncate the length of
            if len(description) > 500:
                description = description[:500]

            link = e.links[0]["href"]
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            # if no image in entry, use the source logo instead
            try:
                imgLink = e.media_content[0]["url"]
            except AttributeError as e:
                imgLink = NewYorker.logo
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data to database!(from %s)" %srcName)

class Wired(BaseParser):
    """
    feed from new york
    """
    logo = "/static/img/logos/wiredLogo.gif"
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            soup = BeautifulSoup(e.description)
            description = jinja2.Markup(soup.getText()).unescape()
            #truncate the length of
            if len(description) > 500:
                description = description[:500]

            link = e.links[0]["href"]
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            # if no image in entry, use the source logo instead
            try:
                imgLink = e.media_content[0]["url"]
            except AttributeError as e:
                imgLink = Wired.logo
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data to database!(from %s)" %srcName)

class NewYorkTimes(BaseParser):
    logo = "/static/img/logos/newyorktimesLogo.gif"
    def parseAndStoreDoc(self):
        for e in self.doc.entries:
            title = jinja2.Markup(e.title).unescape()
            soup = BeautifulSoup(e.description)
            description = jinja2.Markup(soup.getText()).unescape()
            #truncate the length of
            if len(description) > 500:
                description = description[:500]

            link = e.links[0]["href"]
            srcName = self.srcName
            labelName = self.srcName.split("_")[1]
            # if no image in entry, use the source logo instead
            try:
                imgLink = e.media_content[0]["url"]
            except AttributeError as e:
                imgLink = NewYorkTimes.logo
            article = Article(title=title, description=description, imgLink=imgLink, link=link, srcName=srcName, labelName=labelName)
            article.put()
        logging.info("Storing data to database!(from %s)" %srcName)



CACHE = {"washingtonPost_life": {},
         "washingtonPost_opinion": {},
         "time_life": {},
         "time_story" : {},
         "time_opinion": {},
         "time_technology": {},
         "time_travel": {},
         "fhm_woman": {},
         "fhm_man": {},
         "bbc_life": {},
         "bbc_technology": {},
         "bbc_art":{},
         "gq_man": {},
         "wsj_opinion": {},
        "entertainment_woman": {},
        "people_woman": {},
        "reddit_story": {},
        "newYorker_story": {},
        "newYorkTimes_story": {},
        "newYorker_art": {},
        "newYorker_opinion": {},
        "newYorker_books": {},
        "newYorkTimes_art": {},
        "newYorkTimes_books": {},
        "newYorkTimes_travel": {},
        "newYorkTimes_technology": {},
        "wired_technology": {},

         }

def buildCurrentTime():
    """
    some feeds don't have updated_parsed, add it to the article instance
    """
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    return strptime(now)


def retrieveLatest(urlDict):
    "retrieve data by the dict name and I need a label here "
    articles = []
    sub_articles =[]
    innerKey = "top"
    for outerKey in urlDict.keys():
        labelName = outerKey.split("_")[1]
        # if the cache for specific source is not Empty
        if innerKey in CACHE[outerKey]:
            sub_articles = CACHE[outerKey][innerKey]
            logging.info("data is coming from cache, so far so good!")
        else:
            query = "SELECT * FROM Article WHERE srcName = '%s' AND labelName = '%s' limit 30" % (outerKey,labelName)
            queries = db.GqlQuery(query)
            queries = list(queries)
            sub_articles = queries
            CACHE[outerKey][innerKey] = queries
            logging.info("data is coming from datastore,%s" % outerKey)
        articles += sub_articles
    if len(articles) > 100:
        articles = articles[:100]
    shuffle(articles)
    logging.info("the total number of articles is %s" % len(articles))
    return articles

def xmlDispatcher():
    for dictSet in dictBySrc.values():
        for k, v in dictSet.items():
            prefix = k.split("_")[0]
            if prefix == "washingtonPost":
                feedUnit = WashingtonPost(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "time":
                feedUnit = BaseParser(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "fhm":
                feedUnit = FHM(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "bbc":
                feedUnit = BBC(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "gq":
                feedUnit = GQ(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "wsj":
                feedUnit = WSJ(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "entertainment":
                feedUnit = Entertainment(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "people":
                feedUnit = People(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "reddit":
                feedUnit = Reddit(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "newYorker":
                feedUnit = NewYorker(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "newYorkTimes":
                feedUnit = NewYorkTimes(srcName=k, url=v)
                feedUnit.checkUpdated()
            elif prefix == "wired":
                feedUnit = Wired(srcName=k, url=v)
                feedUnit.checkUpdated()
    logging.info("parsing finished!")

def cleanDatastore():

    article = Article.all(keys_only=True)
    db.delete(article)

def runApplication():
    """
        parsing and delete the xml periodically
    """
    #delete
    cleanDatastore()
    #parsring xml
    xmlDispatcher()

