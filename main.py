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
import requests
import urllib

# github
github_api_url = 'https://api.github.com/repos/jfieger/repo-tweet'
github_auth_token = '74c374337f008a53ccd60a253ff4c899ca07de46'  # read-only api access only

# twitter
twitter_account = 'tweettest4234'
twitter_api_url = 'https://api.twitter.com/1.1/search/tweets.json?q=%s' % twitter_account
twitter_bearer_credentials = 'MHJrVllLbzNVcDk3Z2pVT3FKTThCdHR4WDp3YmY1dWpPeGFKbHVsRHVwNlVtUlptV2w3d1NZeVdacWpxcEwwZDJhdUZpQjVhemttNQ=='


def github_get_prs():
    """
        Return a list of strings of the following format:
            <user.login> has created a PR in <base.repo.full_name>: <body> : <html_url>

        If there are no PRs, returns an empty list
    """
    headers = {'Authorization': 'token %s' % github_auth_token}
    r = requests.get('%s/pulls?state=all' % github_api_url, headers=headers)

    prs = []
    # print(r.url)
    if r.status_code == 200:
        data = json.loads(r.content)


        for i in range(0, len(data)):
            # print(data[i]['html_url'])
            login = data[i]['user']['login']
            full_name = data[i]['base']['repo']['full_name']
            body = data[i]['body']
            url = data[i]['html_url']
            pr_string = '%s has created a PR in %s: %s - %s' % (login, full_name, body, url)
            # print(pr_string)
            prs.append(pr_string)
            # <user.login> has created a PR in <base.repo.full_name>: <body> : <html_url>
    else:
        print('ERROR: failed to retrieve github prs')

    return prs


class Twitter():

    def __init__(self):
        self.account = twitter_account
        self.bearer_credentials = twitter_bearer_credentials
        self.set_bearer_token()

    def set_bearer_token(self):
        url = 'https://api.twitter.com/oauth2/token'
        headers = {'Authorization': 'Basic %s' % self.bearer_credentials,
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

    def get_timeline(self):
        """
            :return: return json blob, else None
        """
        if self.bearer_token is None:
            return None

        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?count=100&screen_name=%s' % self.account
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

    def tweet(self, msg):
        """
            POST https://api.twitter.com/1.1/statuses/update.json?status=Maybe%20he%27ll%20finally%20find%20his%20keys.%20%23peterfalk
        """
        print('attempting to tweet the following message: %s' % msg)

        url_data = {'status': msg}
        url = 'https://api.twitter.com/1.1/statuses/update.json?%s' % urllib.urlencode(url_data)
        headers = {'Authorization': 'Bearer %s' % self.bearer_token}
        r = requests.post(url, headers=headers)
        if r.status_code == 200:
            return True
        else:
            print(r.url)
            print(r.status_code)
            print(r.content)
            return False


def main():
    """
        main function, it all starts here
    """
    prs = github_get_prs()

    print('-'*100)

    t = Twitter()
    tweets = t.get_timeline()

    for pr in prs:
        if pr in tweets:
            pass
        else:
            t.tweet(pr)
            # print('pr: %s not found in tweet timeline' % pr)


if __name__ == '__main__':
    main()


