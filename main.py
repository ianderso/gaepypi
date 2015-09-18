import webapp2
import cgi
import cloudstorage

from google.appengine.api import app_identity
from google.appengine.ext.webapp import blobstore_handlers

from models import Package


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body></body></html>')

    def post(self):
        name = self.request.get('name', None)
        version = self.request.get('version', None)
        action = self.request.get(':action', None)

        if action == 'file_upload':
            for key, value in self.request.params.items():
                if isinstance(value, cgi.FieldStorage):
                    uploaded_file = value

            fname = "/{bucket}/{filename}".format(
                bucket=app_identity.get_default_gcs_bucket_name(),
                filename=uploaded_file.filename.strip())

            with cloudstorage.open(fname, 'w') as f:
                f.write(uploaded_file.file.read())
            f.close()
            if name is not None and version is not None:
                pack = Package(name=name,
                               version=version,
                               content=uploaded_file.filename.strip())
                pack.put()


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        if (len(resource) > 0):
            self.send_blob('/gs/' + resource)
        else:
            self.response.write('no id given')


class Listing(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(
            '<html><head><title>eggs</title></head><body><pre>')
        files = Package.query()
        for file in files:
            self.response.out.write(
                '<a href="/gs/{bucket}/{filename}">{filename}</a>\n'.format(
                    bucket=app_identity.get_default_gcs_bucket_name(),
                    filename=file.content))
        self.response.out.write('</pre></body></html>')


class Single(webapp2.RequestHandler):
    def get(self, filename):
        self.response.out.write(
            '<html><head><title>eggs</title></head><body><pre>')
        self.response.out.write(
            '<a href="/gs/{bucket}/{filename}">{filename}</a>\n'.format(
                bucket=app_identity.get_default_gcs_bucket_name(),
                filename=filename))
        self.response.out.write('</pre></body></html>')


app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/simple/(.+)', Single),
                               ('/eggs', Listing),
                               ('/gs/(.+)', ServeHandler)],
                              debug=True)
