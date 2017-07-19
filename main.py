#!/usr/bin/python

"""

    Functions needed:
        RestAPI to request PRs from GitHub
        RestAPI to request tweets from Twitter

        Create a fake PR?

    Operation:
        get latest tweet, parse the commit id
        get github prs that are newer than commit id
        for each PR
            post to twitter

    Test Cases:
        * no PRs exists, don't crash
        * no tweets exist, don't crash
        * no new PRs up, no new tweets
        * 1 new PR, 1 new tweet
        * 3 new PRs, 3 new tweets

"""

import json
import os
import requests

import twitter

PRIVATE_DATA_FILE = 'private.json'

# github
# github_api_url = 'https://api.github.com/repos/jfieger/repo-tweet'
# github_auth_token = '74c374337f008a53ccd60a253ff4c899ca07de46'  # read-only api access only

# twitter
# twitter_account = 'tweettest4234'
# twitter_api_url = 'https://api.twitter.com/1.1/search/tweets.json?q=%s' % twitter_account
# twitter_bearer_credentials = 'MHJrVllLbzNVcDk3Z2pVT3FKTThCdHR4WDp3YmY1dWpPeGFKbHVsRHVwNlVtUlptV2w3d1NZeVdacWpxcEwwZDJhdUZpQjVhemttNQ=='




class GitTwitty():

    def __init__(self):
        self.load_private_data()
        self.twitter_set_bearer_token()

        # self.account = twitter_account
        # self.bearer_credentials = twitter_bearer_credentials
        # self.account = twitter_account
        # self.bearer_credentials = twitter_bearer_credentials

    def load_private_data(self):
        with open(PRIVATE_DATA_FILE) as priv_file:
            self.private_data = json.load(priv_file)

    def github_get_prs(self):
        """
            Return a list of strings of the following format:
                <user.login> has created a PR in <base.repo.full_name>: <body> : <html_url>

            If there are no PRs, returns an empty list
        """
        token = self.private_data['github']['api_token']

        url = 'https://api.github.com/repos/%s' % self.private_data['github']['repo_name']

        headers = {'Authorization': 'token %s' % token}
        r = requests.get('%s/pulls?state=all' % url, headers=headers)

        prs = []
        # print(r.url)
        # print(r.content)
        if r.status_code == 200:
            data = json.loads(r.content)

            if len(data) == 0:
                print("WARNING: no prs found")
            else:
                for i in range(0, len(data)):
                    # print(data[i]['html_url'])
                    login = data[i]['user']['login']
                    full_name = data[i]['base']['repo']['full_name']
                    body = data[i]['body']
                    url = data[i]['html_url']
                    pr_string = '%s has created a pull request in %s: %s - %s' % (login, full_name, body, url)
                    # print(pr_string)
                    prs.append(pr_string)
                    # <user.login> created a pull request in <base.repo.full_name>: <body> : <html_url>
        else:
            print('ERROR: failed to retrieve github prs')

        return prs

    def twitter_set_bearer_token(self):
        url = 'https://api.twitter.com/oauth2/token'
        headers = {'Authorization': 'Basic %s' % self.private_data['twitter']['bearer_credentials'],
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
        data = 'grant_type=client_credentials'
        r = requests.post(url, headers=headers, data=data)

        if r.status_code == 200:
            content = json.loads(r.content)
            if content['token_type'] == 'bearer' and 'access_token' in content:
                # print('successfully got bearer token')
                self.bearer_token = content['access_token']
                # print("bearer_token: %s" % self.bearer_token)
            else:
                self.bearer_token = None
        else:
            print('ERROR: failed to retreive bearer token')
            self.bearer_token = None

    def twitter_get_timeline(self):
        """
            :return: return json blob, else None
        """
        if self.bearer_token is None:
            return None

        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?count=100&screen_name=' + \
              self.private_data['twitter']['screen_name']

        headers = {'Authorization': 'Bearer %s' % self.bearer_token,
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

        r = requests.get(url, headers=headers)
        # print(r.url)
        # print(r.status_code)
        tweets = []
        if r.status_code == 200:
            content = json.loads(r.content)
            for i in range(0, len(content)):
                tweets.append(content[i]['text'])
        else:
            print('ERROR: unable to retrieve timeline')
            print(r.content)

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
        main function, it all starts here
    """

    # check for existence of private data file
    if not os.path.exists(PRIVATE_DATA_FILE):
        print('private data file (%s) does not exist, please copy it here: %s' % (PRIVATE_DATA_FILE,
                                                                                  os.path.realpath(__file__)))
        exit(1)

    t = GitTwitty()

    # get a list of github prs
    prs = t.github_get_prs()

    # print separator
    print('-'*100)

    # get all tweets in the timeline
    tweets = t.twitter_get_timeline()

    # compare github prs to tweets and create a new tweet for each one that's missing missing
    for pr in prs:
        if pr in tweets:
            pass
        else:
            t.twitter_status_update(pr)


if __name__ == '__main__':
    main()


