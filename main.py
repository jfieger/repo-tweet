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

        # we will use this to save state
        self.id_of_last_github_pr = None

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

        number_of_last_pr_tweeted = 0
        if 'last_pr_tweeted' in self.private_data['twitter']:
            number_of_last_pr_tweeted = int(self.private_data['twitter']['last_pr_tweeted'])

        prs = []
        if resp.status_code == 200:
            data = json.loads(resp.content)

            if len(data) == 0:
                print("WARNING: no prs found")
            else:
                for i in range(len(data)-1, -1, -1):
                    full_name = data[i]['base']['repo']['full_name']
                    url = data[i]['html_url']
                    number = data[i]['number']
                    title = data[i]['title']

                    if int(number) > number_of_last_pr_tweeted:
                        pr_string = 'pull request #%s created in %s "%s" %s' % (number, full_name, title, url)
                        prs.append(pr_string)

                    self.id_of_last_github_pr = number
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
        status = api.PostUpdate(msg)

        if 'created_at' in json.loads(status):
            print('success!')

    def update_last_pr(self):
        """
            the attribute id_of_last_github_pr is being tracked in github_get_prs():

            if it exists, then update the private json file with the number
        """
        if self.id_of_last_github_pr:
            self.private_data['twitter']['last_pr_tweeted'] = self.id_of_last_github_pr

            with open(PRIVATE_DATA_FILE, mode='w') as priv_file:
                json.dump(self.private_data, priv_file)


def main():
    """
        Steps:
            Get GitHub pull requests
               If no PRs then exit
               If no PRs newer than the last PR that was tweeted then exit
            Get Twitter timeline
            Compare the two and create tweets for any prs not in the timeline
            Save ID of the last PR to be tweeted

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
    if len(prs) == 0:
        print('no new prs to process')
        exit(0)

    # get all tweets in the timeline
    # TODO: this isn't necessary anymore since I'm tracking the last PR that's been tweeted
    #       but since this code actually utilizes the requests module to interact with twitter's api
    #       and the twitter_status_update does not, I'm leaving it here.
    tweets = gty.twitter_get_timeline()

    # compare github prs to tweets and create a new tweet for each one that's missing missing
    for pull in prs:
        if pull not in tweets:
            gty.twitter_status_update(pull)

    # update private json with the last pr that was tweeted, so that subsequent runs don't repeat work
    gty.update_last_pr()


if __name__ == '__main__':
    main()
