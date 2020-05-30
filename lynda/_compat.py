#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import time
import json
import requests
if sys.version_info[:2] >= (3, 0):

    import ssl
    import urllib.request as compat_urllib

    from urllib.error import HTTPError as compat_httperr
    from urllib.error import URLError as compat_urlerr
    from urllib.parse import urlparse as compat_urlparse
    from urllib.request import Request as compat_request
    from urllib.request import urlopen as compat_urlopen
    from urllib.request import build_opener as compat_opener
    from html.parser import HTMLParser as compat_HTMLParser
    from http.cookies import SimpleCookie as ParseCookie
    from requests.exceptions import ConnectionError as conn_error

    encoding, pyver = str, 3
    ssl._create_default_https_context = ssl._create_unverified_context
    
else:
    
    import urllib2 as compat_urllib

    from urllib2 import Request as compat_request
    from urllib2 import urlopen as compat_urlopen
    from urllib2 import URLError as compat_urlerr
    from urllib2 import HTTPError as compat_httperr
    from urllib2 import build_opener as compat_opener
    from urlparse import urlparse as compat_urlparse
    from HTMLParser import HTMLParser as compat_HTMLParser
    from Cookie import SimpleCookie as ParseCookie
    from requests.exceptions import ConnectionError as conn_error

    encoding, pyver = unicode, 2


NO_DEFAULT = object()

# endpoints for login via email / password
USER_LOGIN_URL = "https://www.lynda.com/signin/lynda"
AJAX_USERNAME = "https://www.lynda.com/signin/user"
AJAX_PASSWORD = "https://www.lynda.com/signin/password"

# endpoints for login via organiztion library card & pin
ORG_LOGIN_URL = "https://www.lynda.com/signin/organization"
AJAX_ORGNIZATION = "https://www.lynda.com/ajax/signin/organization"

# endpoint for logout ..
LOGOUT_URL = "https://www.lynda.com/signout"


COURSE_URL = "https://www.lynda.com/ajax/player?courseId={course_id}&type=course"
VIDEO_URL = "https://www.lynda.com/ajax/course/{course_id}/{video_id}/play"
CAPTIONS_URL = "https://www.lynda.com/ajax/player?videoId={video_id}&type=transcript"
EXERCISE_FILES_URL = "https://www.lynda.com/ajax/course/{course_id}/0/getupselltabs"


HEADERS = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
            'X-Requested-With'  : 'XMLHttpRequest',
            'Host': 'www.lynda.com'
            }


__ALL__ = [
    're',
    'os',
    'sys',
    'time',
    'json',
    'pyver',
    'encoding',
    'requests',
    'conn_error',
    'compat_urlerr',
    'compat_opener',
    'compat_urllib',
    'compat_urlopen',
    'compat_request',
    'compat_httperr',
    'compat_urlparse',
    'compat_HTMLParser',
    'HEADERS',
    'NO_DEFAULT',
    'ParseCookie',

    'USER_LOGIN_URL',
    'AJAX_USERNAME',
    'AJAX_PASSWORD',

    'ORG_LOGIN_URL',
    'AJAX_ORGNIZATION',

    'LOGOUT_URL',

    'COURSE_URL',
    'VIDEO_URL',
    'CAPTIONS_URL',
    'EXERCISE_FILES_URL',
    ]
