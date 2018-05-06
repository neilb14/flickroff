```python
import flickr_api
flickr_api.set_keys(api_key = 'my_api_key', api_secret = 'my_secret')
a = flickr_api.auth.AuthHandler()
url = a.get_authorization_url("read")
print(url)
#verifier = raw_input("Verifier code: ")
a.set_verifier(verifier)
a.save(".flickr_token")
```