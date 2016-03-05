import pytest
from mock import Mock, patch

import foodbornenyc.sources.twitter_search as twitter_search

from foodbornenyc.models.documents import Tweet
from foodbornenyc.models.models import get_db_session
from foodbornenyc.test.generate_test_db import clear_tables
from twython.exceptions import TwythonError

sample = [ {
            'id_str':'2',
            'text':"I hate food!",
            'user': {'id_str': '234'},
            'in_reply_to_user_id_str': None,
            'lang': 'en',
            'created_at': 'Tue Feb 23 23:40:54 +0000 2015',
            'in_reply_to_status_id_str': None,
            'place': None
        }, {
            'id_str':'34',
            'text':"My stomach hurts!",
            'user': {'id_str': '2234'},
            'in_reply_to_user_id_str': None,
            'lang': 'en',
            'created_at': 'Tue Feb 23 21:00:11 +0000 2015',
            'in_reply_to_status_id_str': None,
            'place': None
        }]

def test_make_query():
    """ The correct query should be requested """
    keywords = ['food', 'stomach', 'disease']
    tweets = {'statuses': sample}

    twitter = Mock()
    twitter.search = Mock(return_value=tweets)

    query = twitter_search.make_query(twitter, keywords)

    twitter.search.assert_called_with(q='food OR stomach OR disease')
    assert query == sample

def test_make_query_failed():
    """ If there's an exception, fail gracefully """
    twitter = Mock()
    twitter.search = Mock(side_effect=TwythonError("Can't reach Twitter"))

    query = twitter_search.make_query(twitter, ['food'])

    assert query == []

def test_tweets_to_Tweets():
    """ Sample tweets should be converted properly """
    fields = ['text', 'id_str']
    tweets = twitter_search.tweets_to_Tweets(sample, fields)
    assert_matching_tweets

@patch('foodbornenyc.sources.twitter_search.Twython')
def test_query_twitter(twython):
    """ Database should be filled with tweets returned from Twython """
    clear_tables()

    # make twitter return the sample tweets
    tweet_sequence = [{'statuses': [sample[0]]}, {'statuses': [sample[1]]}]
    twitter = twython.return_value
    twitter.search = Mock(side_effect=tweet_sequence)

    twitter_search.query_twitter(7)

    assert len(twitter.search.call_args_list) == 2
    assert_matching_tweets(get_db_session().query(Tweet).all())

def assert_matching_tweets(tweets):
    """ Helper method for checking if tweets match sample """
    assert len(tweets) == 2
    assert tweets[0].text == sample[0]['text']
    assert tweets[0].id == sample[0]['id_str']
    assert tweets[1].text == sample[1]['text']
    assert tweets[1].id == sample[1]['id_str']

