#!/bin/env python

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

# import requests

GITHUB_REPO = 'https://github.com/jfieger/repo-tweet'
TWITTER_ACCOUNT = 'jfieger/repo-tweet'


def github_get_prs():
    pass


def twitter_get_tweets(count=0):
    '''
        :param count:  number of tweets to retreive
        :return:  list of tweets
    '''
    pass


def main():
    '''
        main function, it all starts here
    '''
    pass


if __name__ == '__main__':
    main()


