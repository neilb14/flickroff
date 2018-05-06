# What is this?
I needed a way to download all photos in sets from Flickr. This is the script.

# Getting Started
Make sure you register for Flickr API keys. Google it, or wait patiently and I'll add the right link when I have a chance.

Then run the following steps in Python console:
```python
import flickr_api
flickr_api.set_keys(api_key = 'my_api_key', api_secret = 'my_secret')
a = flickr_api.auth.AuthHandler()
url = a.get_authorization_url("read")
print(url)
# go visit that url and accept the token
# then copy and paste the oauth_verifier field below
a.set_verifier('oauth_verifier field')
a.save(".flickr_token")
```

It needs to be the console because you need the same session in your AuthHandler between creating and accepting the Oauth token.


