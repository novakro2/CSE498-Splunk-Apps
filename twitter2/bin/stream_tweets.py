#!/usr/bin/env python
#
# Copyright 2012 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, sofaare
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Scripted input that streams data from Twitter's 1% sample feed to standard
output, with each event on a separate line in JSON format.

The original JSON from Twitter is augmented with an extra '__time' key on each
event. This makes it possible for Splunk to use a regex to parse out the
timestamp accurately.

This script can be used as a standalone command-line program or imported as a
module and invoked directly via either the `start` method or the
`read_sample_tweet_stream` method.
"""

from twython import TwythonStreamer

import json
import splunk
import splunklib.client
import sys
import traceback


class TweetStreamer(TwythonStreamer):
    """
    Collects and writes a stream of tweets from Twitter
    """

    def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret,
                 timeout=300, retry_count=None, retry_in=10, headers=None,
                 output_stream=None):
        super(TweetStreamer, self).__init__(
            app_key, app_secret, oauth_token, oauth_token_secret, timeout,
            retry_count, retry_in, headers)
        self._output_stream = \
            sys.stdout if output_stream is None else output_stream

    def on_error(self, status_code, data):
        sys.stderr.write(
            'Twitter reported status code %d: %s' % (status_code, data))
        sys.stderr.flush()

    def on_limit(self, limit):
        sys.stderr.write(
            'More Tweets matched than the Twitter rate limit allows. %d ' +
            'undelivered Tweets since the connection was opened.\n' %
            limit['track'])

    def on_success(self, data):
        # Super calls our other handlers using rules we'd like not to duplicate
        super(TweetStreamer, self).on_success(data)

        if 'created_at' in data:
            # Generate a synthetic field with the desired timestamp so that
            # Splunk can accurately parse it
            data['__time'] = data['created_at']

        # Preserve compact output format with separators
        json.dump(data, self._output_stream,
            # Preserve compact output format
            separators=(',', ':'),
            # Workaround issue where searching for \u####-encoded characters
            # doesn't work. (DVPL-2401)
            ensure_ascii=False)

        self._output_stream.write('\r\n')


def get_oauth_settings(session_key):
    """
    Retrieves OAuth settings from args.

    :param session_key: A value identifying the current Splunk session.
    :return: OAuth settings tuple: 'app_key', 'app_secret', 'oauth_token', and
    'oauth_token_secret'
    """

    # NOTE: Requires 'develop' version of splunklib past 0.8.0 for 'token'
    # parameter to be honored
    service = splunklib.client.Service(
        host=splunk.getDefault('host'),
        port=splunk.getDefault('port'),
        scheme=splunk.getDefault('protocol'),
        owner='nobody',
        app='twitter2',
        token='Splunk %s' % session_key)

    passwords = splunklib.client.Collection(service, 'admin/passwords')
    oauth_settings = None

    for password in passwords:
        oauth_settings = password
        break

    if oauth_settings is None:
        sys.stderr.write(
            'Could not retrieve Twitter OAuth settings from Splunk. Set up ' +
            'the app to correct this issue.\n')
        exit(1)

    app_key = oauth_settings.content['realm']
    oauth_token = oauth_settings.content['username']
    secrets = oauth_settings.content['clear_password']

    if None in (app_key, oauth_token, secrets):
        sys.stderr.write(
            'Splunk returned incomplete Twitter OAuth settings. Set up the ' +
            'app to correct this issue.\n')
        exit(1)

    try:
        (app_secret, oauth_token_secret) = secrets.split(':')
    except ValueError as e:
        sys.stderr.write(
            'Could not parse the Twitter OAuth secrets returned by Splunk: '
            '%s. Set up the app to correct this issue.\n' % e.message)
        exit(1)

    return app_key, app_secret, oauth_token, oauth_token_secret


def read_sample_tweet_stream(
    app_key, app_secret, oauth_token, oauth_token_secret, output_stream=None
):
    """
    Continuously reads tweets from the sample Twitter stream and writes them to
    the specified output stream or `sys.stdout`, if no stream is provided.

    Never returns, unless an I/O error occurs.

    :param app_key:                 Twitter application consumer key
    :param app_secret:              Twitter application consumer secret
    :param oauth_token:             Twitter application access token
    :param oauth_token_secret:      Twitter application access token secret
    :param output_stream:           (optional) A file-like object to which data
                                    will be written.
                                    Must support a `write` method. Defaults to
                                    `sys.stdout`.
    :raises KeyboardInterrupt       If you stop the tweet stream using
    Control-C.
    :raises TwythonAuthError:       If the tweet stream stops due to some issue
                                    with your authentication.
    :raises TwythonRateLimitError:  If the tweet stream stops because you hit a
                                    rate limit.
    :raises TwythonError:           If the tweet stream stops for any other
                                    reason.
    """

    streamer = TweetStreamer(
        app_key=app_key,
        app_secret=app_secret,
        oauth_token=oauth_token,
        oauth_token_secret=oauth_token_secret,
        output_stream=output_stream
    )

    streamer.statuses.sample()


def start(app_key, app_secret, oauth_token, oauth_token_secret,
          output_stream=None):
    """
    Continuously reads tweets from the sample Twitter stream and writes them to
    the specified output stream or `sys.stdout`, if no stream is provided.

    Never returns, unless an I/O error occurs.

    :param app_key:                 Twitter application consumer key
    :param app_secret:              Twitter application consumer secret
    :param oauth_token:             Twitter application access token
    :param oauth_token_secret:      Twitter application access token secret
    :param output_stream:           (optional) A file-like object to which data
                                    will be written.
                                    Must support a `write` method. Defaults to
                                    `sys.stdout`.
    :raises TwythonAuthError:       If the tweet stream stops due to some issue
                                    with your authentication.
    :raises TwythonRateLimitError:  If the tweet stream stops because you hit a
                                    rate limit.
    :raises TwythonError:           If the tweet stream stops for any other
                                    reason.
    """

    try:
        read_sample_tweet_stream(
            app_key, app_secret, oauth_token, oauth_token_secret, output_stream)
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise


def main():
    session_key = sys.stdin.readline().strip()

    if len(session_key) == 0:
        sys.stderr.write(
            'Did not receive a session key from splunkd. Please enable ' +
            'passAuth in inputs.conf for this script.\n')
        exit(2)

    app_key, app_secret, oauth_token, oauth_token_secret = \
        get_oauth_settings(session_key)

    start(
        app_key=app_key,
        app_secret=app_secret,
        oauth_token=oauth_token,
        oauth_token_secret=oauth_token_secret)


if __name__ == '__main__':
    main()
