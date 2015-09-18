from google.appengine.ext import ndb


class Package(ndb.Model):
    name = ndb.StringProperty()
    version = ndb.StringProperty()
    content = ndb.StringProperty()
