#!/usr/bin/python

from __future__ import print_function

import json
import os
import requests

import twitter

PRIVATE_DATA_FILE = 'private.json'

# pylint: disable=C0301


class GitTwitty():
    """
        Class for handing both GitHub and Twitter APIs

        The reason this is a single class is that they both load the private data file
    """

    def __init__(self):
        self.private_data = self.load_private_data()
        self.twitter_bearer_token = self.twitter_get_bearer_token()

    @staticmethod
    def load_private_data():
        """
            load sensitive data for github and twitter accounts
        """
        with open(PRIVATE_DATA_FILE) as priv_file:
            return json.load(priv_file)

    def github_get_prs(self):
        """
            Return a list of strings of the following format:
            <user> has created a pull request in <repo>: <pr text> : <html_url>

            If there are no PRs, returns an empty list
        """
        token = self.private_data['github']['api_token']

        url = 'https://api.github.com/repos/%s' % self.private_data['github']['repo_name']

        headers = {'Authorization': 'token %s' % token}
        resp = requests.get('%s/pulls?state=all' % url, headers=headers)

        prs = []
        if resp.status_code == 200:
            data = json.loads(resp.content)

            if len(data) == 0:
                print("WARNING: no prs found")
            else:
                for i in range(0, len(data)):
                    login = data[i]['user']['login']
                    full_name = data[i]['base']['repo']['full_name']
                    body = data[i]['body']
                    url = data[i]['html_url']
                    pr_string = '%s has created a pull request in %s: %s - %s' % (login, full_name, body, url)
                    prs.append(pr_string)
        else:
            print('ERROR: failed to retrieve github prs')

        return prs

    def twitter_get_bearer_token(self):
        """
            use basic auth to generate the bearer token that the application api requires
        """
        url = 'https://api.twitter.com/oauth2/token'
        headers = {'Authorization': 'Basic %s' % self.private_data['twitter']['bearer_credentials'],
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
        data = 'grant_type=client_credentials'
        resp = requests.post(url, headers=headers, data=data)

        if resp.status_code == 200:
            content = json.loads(resp.content)
            if content['token_type'] == 'bearer' and 'access_token' in content:
                return content['access_token']
            else:
                return None
        else:
            print('ERROR: failed to retreive bearer token')
            return None

    def twitter_get_timeline(self):
        """
            get the entire timeline and return a list with the text contents of each tweet
        """
        if self.twitter_bearer_token is None:
            return None

        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?count=100&screen_name=' + \
              self.private_data['twitter']['screen_name']

        headers = {'Authorization': 'Bearer %s' % self.twitter_bearer_token,
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

        resp = requests.get(url, headers=headers)
        tweets = []
        if resp.status_code == 200:
            content = json.loads(resp.content)
            for i in range(0, len(content)):
                tweets.append(content[i]['text'])
        else:
            print('ERROR: unable to retrieve timeline')
            print(resp.content)

        return tweets

    def twitter_status_update(self, msg):
        """
            Use python-twitter library since the user oauth is a huge undertaking to implement
        """
        print('updating twitter status with message: %s' % msg)

        api = twitter.Api(**self.private_data['twitter']['keys'])
        print(api.VerifyCredentials())
        status = api.PostUpdate(msg)

        print(status)


def main():
    """
        Steps:
            Get GitHub pull requests
            Get Twitter timeline
            Compare the two and create tweets for any prs not in the timeline

        Usage:
            save a copy of private data to: private.json
            python main.py
    """

    # check for existence of private data file
    if not os.path.exists(PRIVATE_DATA_FILE):
        print('private data file (%s) does not exist, please copy it here: %s' % (PRIVATE_DATA_FILE,
                                                                                  os.path.realpath(__file__)))
        exit(1)

    # our GitHub+Twitter handler
    gty = GitTwitty()

    # get a list of github prs
    prs = gty.github_get_prs()

    # get all tweets in the timeline
    tweets = gty.twitter_get_timeline()

    # compare github prs to tweets and create a new tweet for each one that's missing missing
    for pull in prs:
        if pull in tweets:
            pass
        else:
            gty.twitter_status_update(pull)


if __name__ == '__main__':
    main()
