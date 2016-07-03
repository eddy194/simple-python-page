#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
import hashlib, uuid

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START signature]
class Signature(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)
    dob = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    pwd = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END signature]


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_first_name = self.request.get('guestbook_first_name')
        guestbook_last_name = self.request.get('guestbook_last_name')
        guestbook_dob = self.request.get('guestbook_dob')
        guestbook_email = self.request.get('guestbook_email')
        guestbook_pwd = self.request.get('guestbook_pwd')
        signatures_array = []
        signatures =  Signature.query().fetch(20,keys_only=True)
        for signature in signatures:
            signature_object = signature.get()
            temp_signature = Signature(first_name = signature_object.first_name,
                                     last_name = signature_object.last_name,
                                     dob = signature_object.dob,
                                     email = signature_object.email,
                                     pwd = signature_object.pwd)
            signatures_array.append(temp_signature)
        template_values = {
            'signatures': signatures_array,
            'guestbook_first_name': urllib.quote_plus(guestbook_first_name),
            'guestbook_last_name': urllib.quote_plus(guestbook_last_name),
            'guestbook_dob': urllib.quote_plus(guestbook_dob),
            'guestbook_email': urllib.quote_plus(guestbook_email),
            'guestbook_pwd': urllib.quote_plus(guestbook_pwd),
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START guestbook]
class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'signature' to ensure each
        # signature is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_first_name = self.request.get('guestbook_first_name')
        guestbook_last_name = self.request.get('guestbook_last_name')
        guestbook_dob = self.request.get('guestbook_dob')
        guestbook_email = self.request.get('guestbook_email')
        guestbook_pwd = self.request.get('guestbook_pwd')

        query_params = {'guestbook_first_name': guestbook_first_name,
                        'guestbook_last_name': guestbook_last_name,
                        'guestbook_dob': guestbook_dob,
                        'guestbook_email': guestbook_email,
                        'guestbook_pwd': guestbook_pwd
                        }
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(guestbook_pwd + salt).hexdigest()
        new_entry = Signature(first_name=guestbook_first_name,
                             last_name=guestbook_last_name,
                             dob=guestbook_dob,
                             email=guestbook_email,
                             pwd=hashed_password)
        new_entry.put()
        self.redirect('/')
# [END guestbook]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)
# [END app]
