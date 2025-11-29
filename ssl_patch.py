"""SSL patch for InsightFace model downloads."""
import ssl
import urllib.request

# Disable SSL verification for model downloads
ssl._create_default_https_context = ssl._create_unverified_context

# Patch urllib to use unverified context
original_urlopen = urllib.request.urlopen

def patched_urlopen(*args, **kwargs):
    if 'context' not in kwargs:
        kwargs['context'] = ssl._create_unverified_context()
    return original_urlopen(*args, **kwargs)

urllib.request.urlopen = patched_urlopen

