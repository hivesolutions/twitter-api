#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Twitter API
# Copyright (c) 2008-2024 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from . import search
from . import account
from . import streaming

BASE_URL = "https://api.twitter.com/"
""" The default base URL to be used when no other
base URL value is provided to the constructor """

CLIENT_KEY = None
""" The default value to be used for the client key
in case no client key is provided to the API client """

CLIENT_SECRET = None
""" The secret value to be used for situations where
no client secret has been provided to the client """

REDIRECT_URL = "http://localhost:8080/oauth"
""" The redirect URL used as default (fallback) value
in case none is provided to the API (client) """


class API(
    appier.OAuth1API, search.SearchAPI, account.AccountAPI, streaming.StreamingAPI
):

    def __init__(self, *args, **kwargs):
        appier.OAuth1API.__init__(self, *args, **kwargs)
        self.client_key = appier.conf("TWITTER_KEY", CLIENT_KEY)
        self.client_secret = appier.conf("TWITTER_SECRET", CLIENT_SECRET)
        self.redirect_url = appier.conf("TWITTER_REDIRECT_URL", REDIRECT_URL)
        self.base_url = kwargs.get("base_url", BASE_URL)
        self.client_key = kwargs.get("client_key", self.client_key)
        self.client_secret = kwargs.get("client_secret", self.client_secret)
        self.redirect_url = kwargs.get("redirect_url", self.redirect_url)
        self.oauth_token = kwargs.get("oauth_token", None)
        self.oauth_token_secret = kwargs.get("oauth_token_secret", None)

    def oauth_request(self, state=None):
        url = self.base_url + "oauth/request_token"
        redirect_url = self.redirect_url
        if state:
            redirect_url += "?state=%s" % appier.quote(state, safe="~")
        contents = self.post(url, oauth_callback=redirect_url)
        contents = contents.decode("utf-8")
        contents = appier.legacy.parse_qs(contents)
        self.oauth_token = contents["oauth_token"][0]
        self.oauth_token_secret = contents["oauth_token_secret"][0]

    def oauth_authorize(self, state=None):
        self.oauth_request(state=state)
        url = self.base_url + "oauth/authorize"
        values = dict(oauth_token=self.oauth_token)
        data = appier.legacy.urlencode(values)
        url = url + "?" + data
        return url

    def oauth_access(self, oauth_verifier=None):
        url = self.base_url + "oauth/access_token"
        kwargs = dict()
        if oauth_verifier:
            kwargs["oauth_verifier"] = oauth_verifier
        contents = self.post(url, **kwargs)
        contents = contents.decode("utf-8")
        contents = appier.legacy.parse_qs(contents)
        self.oauth_token = contents["oauth_token"][0]
        self.oauth_token_secret = contents["oauth_token_secret"][0]
        self.trigger("oauth_token", self.oauth_token)
        return (self.oauth_token, self.oauth_token_secret)
