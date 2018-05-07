import sys, flickr_api

def main(args):
    if(len(args) <= 1):        
        print("Usage: authenticate API_KEY API_SECRET")
        return -1
    key,secret = sys.argv[1], sys.argv[2]
    flickr_api.set_keys(api_key = key, api_secret = secret)
    a = flickr_api.auth.AuthHandler()
    url = a.get_authorization_url("read")
    print('Visit the following: {}'.format(url))
    verifier = input("Verifier code: ")
    a.set_verifier(verifier)
    a.save(".flickr_token")

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))