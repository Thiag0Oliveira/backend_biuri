"""
Created on 04/sep/2016
@author: Marco Pompili
"""

from socket import error as socket_error
from lxml import html
import requests
from requests.exceptions import ConnectionError, HTTPError
import json
import logging

SCRIPT_JSON_PREFIX = 18
SCRIPT_JSON_DATA_INDEX = 21


def instagram_scrap_profile(username, hashtag=''):
    """
    Scrap an instagram profile page
    :param username:
    :param hashtag:
    :return:
    """
    try:
        if hashtag:
            url = "https://www.instagram.com/explore/tags/{}/".format(hashtag)
        else:
            url = "https://www.instagram.com/{}/".format(username)
        page = requests.get(url)
        # Raise error for 404 cause by a bad profile name
        page.raise_for_status()
        return html.fromstring(page.content)
    except HTTPError:
        logging.exception('user profile "{}" not found'.format(username))
    except (ConnectionError, socket_error) as e:
        logging.exception("instagram.com unreachable")


def instagram_profile_js(username, hashtag = ''):
    """
    Retrieve the script tags from the parsed page.
    :param username:
    :return:
    """
    try:
        tree = instagram_scrap_profile(username, hashtag)
        return tree.xpath('//script')
    except AttributeError:
        logging.exception("scripts not found")
        return None


def instagram_profile_json(username, hashtag = ''):
    """
    Get the JSON data string from the scripts.
    :param username:
    :return:
    """
    scripts = instagram_profile_js(username, hashtag)
    source = None

    if scripts:
        for script in scripts:
            if script.text:
                if script.text[0:SCRIPT_JSON_PREFIX] == "window._sharedData":
                    source = script.text[SCRIPT_JSON_DATA_INDEX:-1]

    return source


def instagram_profile_obj(username, hashtag):
    """
    Retrieve the JSON from the page and parse it to a python dict.
    :param username:
    :return:
    """
    json_data = instagram_profile_json(username, hashtag)
    return json.loads(json_data) if json_data else None


def get_user_information(username, hashtag = ''):
    user = instagram_profile_obj(username, hashtag)
    return user['entry_data']['ProfilePage'][0]['graphql']['user']