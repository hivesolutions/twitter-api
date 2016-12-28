#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Twitter API
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Twitter API.
#
# Hive Twitter API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Twitter API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Twitter API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from . import base

class TwitterApp(appier.WebApp):

    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(
            self,
            name = "twitter",
            *args, **kwargs
        )

    @appier.route("/", "GET")
    def index(self):
        return self.me()

    @appier.route("/me", "GET")
    def me(self):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        account = api.verify_account()
        return account

    @appier.route("/streaming", "GET")
    def streaming(self):
        url = self.ensure_api()
        if url: return self.redirect(url)
        api = self.get_api()
        streaming = api.user_streaming()
        return streaming

    @appier.route("/search", "GET")
    def search(self):
        url = self.ensure_api()
        if url: return self.redirect(url)
        query = self.field("query", "Hive")
        api = self.get_api()
        results = api.tweets_search(query)
        return results

    @appier.route("/oauth", "GET")
    def oauth(self):
        oauth_verifier = self.field("oauth_verifier")
        api = self.get_api()
        oauth_token, oauth_token_secret = api.oauth_access(oauth_verifier)
        self.tokens(oauth_token, oauth_token_secret, temporary = False)
        return self.redirect(
            self.url_for("twitter.index")
        )

    @appier.exception_handler(appier.OAuthAccessError)
    def oauth_error(self, error):
        self.delete()
        return self.redirect(
            self.url_for("twitter.index")
        )

    def ensure_api(self):
        oauth_token = self.session.get("tw.oauth_token", None)
        oauth_token_secret = self.session.get("tw.oauth_token_secret", None)
        oauth_temporary = self.session.get("tw.oauth_temporary", True)
        if not oauth_temporary and oauth_token and oauth_token_secret: return
        self.invalidate()
        api = base.get_api()
        url = api.oauth_authorize()
        self.tokens(api.oauth_token, api.oauth_token_secret, temporary = True)
        return url

    def get_api(self):
        oauth_token = self.session and self.session.get("tw.oauth_token", None)
        oauth_token_secret = self.session and self.session.get("tw.oauth_token_secret", None)
        api = base.get_api()
        api.oauth_token = oauth_token
        api.oauth_token_secret = oauth_token_secret
        return api

    def tokens(self, oauth_token, oauth_token_secret, temporary = True):
        self.session["tw.oauth_token"] = oauth_token
        self.session["tw.oauth_token_secret"] = oauth_token_secret
        self.session["tw.oauth_temporary"] = temporary

    def invalidate(self):
        self.tokens(None, None, temporary = True)

    def delete(self):
        if "tw.oauth_token" in self.session: del self.session["tw.oauth_token"]
        if "tw.oauth_token_secret" in self.session: del self.session["tw.oauth_token_secret"]
        if "tw.oauth_temporary" in self.session: del self.session["tw.oauth_temporary"]

if __name__ == "__main__":
    app = TwitterApp()
    app.serve()
else:
    __path__ = []
