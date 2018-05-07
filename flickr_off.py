#!/usr/bin/env python
import os,sys,yaml,argparse,time
import flickr_api
import flickr_api as Flickr
import logging
from flickr_api.flickrerrors import FlickrError, FlickrAPIError
from dateutil import parser

KEY_FILE = ".flickr_keys"
OAUTH_FILE = ".flickr_token"

def sanitize_filepath(fname):
    """
    Ensure that a file path does not have path name separators in it.
    @param fname: str, path to sanitize
    @return: str, sanitized path
    """
    ret = fname.replace(os.path.sep, '_')
    if os.path.altsep:
        ret = ret.replace(os.path.altsep, '_')
    return ret

def get_full_path(path, pset, photo):
    """
    Assemble a full path from the photoset and photo titles
    @param pset: str, photo set name
    @param photo: str, photo name
    @return: str, full sanitized path
    """
    return os.path.join(path, sanitize_filepath(pset), sanitize_filepath(photo))

def get_photo_page(photo_info):
    """
    Get the photo page URL from a photo info object
    """
    ret = ''
    if photo_info.get('urls') and photo_info['urls'].get('url'):
        for url in photo_info['urls']['url']:
            if url.get('type') == 'photopage':
                ret = url.get('text')
    return ret

def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)

def configure():
    filename = os.path.expanduser(KEY_FILE)
    with open(filename, 'r') as cfile:
        vals = yaml.load(cfile.read())
    flickr_api.set_keys(**vals)
    flickr_api.set_auth_handler(OAUTH_FILE)

def list_sets():
    user = flickr_api.test.login()
    photosets = user.getPhotosets()
    for photo in photosets:
        print('{0} - {1}'.format(photo.id, photo.title))

def download_set(set_id, path):
    print('Downloading Set: {} into {}'.format(set_id, path))
    pset = Flickr.Photoset(id=set_id)
    photos = pset.getPhotos()
    pagenum = 2
    while True:
        try:
            if pagenum > photos.info.pages:
                break
            page = pset.getPhotos(page=pagenum)
            photos.extend(page)
            pagenum += 1
        except FlickrAPIError as ex:
            if ex.code == 1:
                break
            raise
    dirname = pset.title.replace(os.sep, "_")
    ensure_dir_exists(os.path.join(path,dirname))

    for photo in photos:
        download_photo(path, dirname, pset, photo)

def download_photo(path, dirname, pset, photo):
    fname = get_full_path(path, dirname, photo.id)
    pInfo = photo.getInfo()
    
    photo_size_label = None
    if 'video' in pInfo:
        pSizes = photo.getSizes()
        if 'HD MP4' in pSizes:
            photo_size_label = 'HD MP4'
        else:
            # Fall back for old 'short videos'
            photo_size_label = 'Site MP4'
        fname = fname + '.mp4'

    if os.path.exists(fname):
        # TODO: Ideally we should check for file size / md5 here
        # to handle failed downloads.
        print('Skipping {0}, as it exists already'.format(fname))
        return

    print('Saving: {} ({})'.format(fname, get_photo_page(pInfo)))
    
    try:
        photo.save(fname, photo_size_label)
    except IOError as ex:
        logging.warning('IO error saving photo: {}'.format(ex.strerror))
        return
    except FlickrError as ex:
        logging.warning('Flickr error saving photo: {}'.format(str(ex)))
        return

    # Set file times to when the photo was taken
    taken = parser.parse(pInfo['taken'])
    taken_unix = time.mktime(taken.timetuple())
    os.utime(fname + '.jpg', (taken_unix, taken_unix))
    

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Downloads one or more Flickr photo sets.\n'
        '\n'
        'Create a ' + KEY_FILE + ' in this directory and drop your API key and secret like so:\n'
        '  api_key: .....\n'
        '  api_secret: ...\n'
        'Make sure you run authenticate.py to create ' + OAUTH_FILE + ' in this directory.',
        epilog='usage:\n'
        '  list all sets:\n'
        '  > {app} -l\n'
        '\n'
        '  download a given set:\n'
        '  > {app} -d 72157602180187398\n'
        .format(app=sys.argv[0])
    )
    parser.add_argument('-l', '--list', action='store_true', help='List sets')
    parser.add_argument('-d', '--download', type=str, metavar='SET_ID', help='Download the given set')
    parser.add_argument('-p', '--path', type=str, metavar='PATH', default='downloads', help='Path to download images into')
    args = parser.parse_args()
    configure()
    if(args.list):
        list_sets()
        return 0
    if(args.download):
        ensure_dir_exists(args.path)
        download_set(args.download, args.path)
        return -1
    print('ERROR: Must pass either --list or --download\n', file=sys.stderr)
    parser.print_help()
    return 1

if __name__ == '__main__':
    sys.exit(main())