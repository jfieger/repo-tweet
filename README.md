# repo-tweet
A tool which sends notifications via twitter for PRs posted in the repository


## Objective
HTTP Integration with GitHub and Twitter
Write a program that will poll a GitHub repo, look for new pull requests, and tweet a summary of each PR to Twitter. Some practical considerations:
* A dummy github repo should be created and API access be enabled
* A dummy twitter account should be created and API access should be enabled
* Getting the PRs via webhook might be impractical (especially considering that we should be able to easily run and test your program). Suggestion: the program can start up, gather the latest PR's, post them to Twitter, then exit. Subsequent runs of the program should pick up PR's that have come in since the last time. (How will you persist the state between runs?) .... Alternately, the program can run forever and periodically poll the GitHub repo for changes.

## Constraints
* Make plain HTTP requests against GitHub and Twitter, i.e., do not use a 3rd party Github or Twitter SDK for Python. The python requests library is recommended (http://docs.python-requests.org/en/master/


## Installation / Setup (tested on MacOS)
pip install virtualenv
virtualenv ENV
cd ENV
source bin/activate
pip install -r requirements.txt

**Note** if a virtual environment isn't available or not desired, only the last step is needed.


## Running the test
python main.py