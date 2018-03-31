#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Admiralspark'
SITENAME = u'Ignition'
SITEURL = 'http://teamignition.us'

PATH = 'content'

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Plugins
PLUGIN_PATHS = ['/home/admiralspark/pelican-plugins']
PLUGINS = ['i18n_subsites']

# Main site options
USE_FOLDER_AS_CATEGORY = True
DEFAULT_CATEGORY = 'misc'
DISPLAY_CATEGORIES_ON_MENU = True
DISPLAY_PAGES_ON_MENU = True
SHOW_ARTICLE_CATEGORY = True
DELETE_OUTPUT_DIRECTORY = True
SLUGIFY_SOURCE = 'title'
DISPLAY_ARTICLE_INFO_ON_INDEX = True
DISPLAY_RECENT_POSTS_ON_SIDEBAR = True
NEWEST_FIRST_ARCHIVES = True

# Banner items for theme
BANNER = 'images/banner.png'
BANNER_ALL_PAGES = True
BANNER_SUBTITLE = 'Eat. Sleep. Code. Repeat.'

# Themes
THEME = "/home/admiralspark/pelican-themes/pelican-bootstrap3"
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
BOOTSTRAP_THEME = 'lumen'

# For Testing purposes
LOAD_CONTENT_CACHE = True

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
