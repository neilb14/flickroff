#!/usr/bin/env python
import os,sys,yaml
import flickr_api
import flickr_api as Flickr
from flickr_api.flickrerrors import FlickrError, FlickrAPIError

KEY_FILE = ".flickr_keys"
OAUTH_FILE = ".flickr_token"

def authenticate():
    filename = os.path.expanduser(KEY_FILE)
    with open(filename, 'r') as cfile:
        vals = yaml.load(cfile.read())
    flickr_api.set_keys(**vals)
    flickr_api.set_auth_handler(OAUTH_FILE)

def main(args):
    authenticate()
    user = flickr_api.test.login()
    photosets = user.getPhotosets()
    for photo in photosets:
        print('{0} - {1}'.format(photo.id, photo.title))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))