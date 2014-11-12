import urllib
import webapp2
import cgi

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import files

from models import Package

import logging
class MainHandler(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.response.out.write('<html><body></body></html>')

    def post(self):
        name = self.request.get('name', None)
        version = self.request.get('version', None)
        action = self.request.get(':action', None)
        logging.info(self.request.params)
        if action == 'file_upload':
            for key, value in self.request.params.items():
                if isinstance(value, cgi.FieldStorage):
                    uploaded_file = value

            fname = uploaded_file.filename.strip()
            file_name = files.blobstore.create(
                _blobinfo_uploaded_filename=fname)
            with files.open(file_name, 'a') as f:
                f.write(uploaded_file.file.read())
            files.finalize(file_name)

            blob_key = files.blobstore.get_blob_key(file_name)
            if name is not None and version is not None:
                pack = Package(name=name, version=version, content=blob_key)
                pack.put()


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.gql(
            "WHERE filename='%s' LIMIT 1" % resource)[0]
        self.send_blob(blob_info, save_as=True)


class Listing(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(
            '<html><head><title>eggs</title></head><body><pre>')
        files = blobstore.BlobInfo.all()
        for file in files:
            self.response.out.write(
                '<a href="{filename}">{filename}</a>\n'.format(
                    filename=file.filename))
        self.response.out.write('</pre></body></html>')


class Single(webapp2.RequestHandler):
    def get(self, filename):
        self.response.out.write(
            '<html><head><title>eggs</title></head><body><pre>')
        blob_info = blobstore.BlobInfo.gql(
            "WHERE filename > '%s' LIMIT 1" % filename)[0]
        self.response.out.write(
            '<a href="{filename}">{filename}</a>\n'.format(
                filename=blob_info.filename))
        self.response.out.write('</pre></body></html>')


app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/simple/(.+)', Single),
                               ('/eggs', Listing),
                               ('/([^/]+)?', ServeHandler)],
                              debug=True)
