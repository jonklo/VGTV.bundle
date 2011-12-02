# -*- coding: utf-8 -*-
import random
import re

BASE_URL_FEED = 'http://www.vgtv.no/api/'
PLAYLIST_NAMESPACE = {'ns1': 'http://xspf.org/ns/0/'}
CACHE_HTML_INTERVAL = 3600 * 5
ICON = 'icon-default.png'
NAMESPACES = {'x': 'http://www.aptoma.no/produkt/tv/xmlns'}


def MostViewedMenu(sender):
    return VideoListMenu(sender, vtype='mostseen')

def RecentlyAddedMenu(sender):
    return VideoListMenu(sender, vtype='latest')

def CategoriesMenu(sender, subcategories=None):
    """
    Displays categories and sub categories from a feed.
    """
    dir = MediaContainer(title2=sender.itemTitle)

    # Sub categories
    if subcategories:
        for cat in subcategories:
            #Log(cat)
            dir.Append(Function(DirectoryItem(VideoListMenu, title=cat['title']), id=cat['id']))
        return dir


    # Fetch all top level categories
    url = '%s?do=feed&action=categories' % BASE_URL_FEED
    rss = HTTP.Request(url, cacheTime=CACHE_HTML_INTERVAL).content
    rss = re.sub('&(?!amp;)', '&amp;', rss)
    rss = HTML.ElementFromString(rss)
    categories = rss.xpath('//categories/item')

    # Display error message if no categories are found
    if not len(categories):
        return (MessageContainer(header=L('title'), message=L('podcast_noepisodes')))

    for cateogory in categories:
        title = cateogory.xpath('./name/text()')[0]
        id = cateogory.xpath('./id/text()')[0]
        raw_subcategories = cateogory.xpath('./subcategories')[0]

        subcategories = []

        for cat in raw_subcategories:
            subcategories.append({
                'id': cat.xpath('./id/text()')[0], 
                'title': cat.xpath('./name/text()')[0],
            })

        dir.Append(Function(DirectoryItem(CategoriesMenu, title=title), subcategories=subcategories))

    return dir

def VideoListMenu(sender, vtype='category', id=None):
    """
    Displays a list of video clips.
    """
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList')

    url = '%s?do=feed&action=%s&value=%s&limit=25' % (BASE_URL_FEED, vtype, id)
    rss = XML.ElementFromURL(url, cacheTime=CACHE_HTML_INTERVAL)

    videos = rss.xpath('//item')

    # Display error message if no categories are found
    if not len(videos):
        return (MessageContainer(header=L('title'), message=L('noepisodes')))

    for item in videos:
        title = item.xpath('./title/text()')[0]
        clip_id = item.xpath('./x:id/text()', namespaces=NAMESPACES)[0]

        try:
            img_url = item.xpath('./enclosure')[0].get('url').replace('_160px', '_640px')
        except:
            img_url = None

        try:
            desc = item.xpath('./description/text()')[0]
            desc = String.StripTags(desc)
        except:
            desc = None

        player_url, clip_url = get_player_and_clip_url(clip_id)

        if player_url and clip_url:
            dir.Append(RTMPVideoItem(url=player_url, clip=clip_url, title=title, summary=desc, thumb=Function(get_thumb, url=img_url)))

    return dir


###########
# Helpers #
###########

def get_player_and_clip_url(id):
    """
    Fetches and separates the player and clip urls.
    """

    url = 'http://www.vgtv.no/data/actions/videostatus/?id=%s' % id

    resp = JSON.ObjectFromURL(url)

    if 'formats' in resp:
        try:
            paths = resp['formats']['rtmp']['mp4'][0]['paths']
        except:
            paths = resp['formats']['rtmp']['flv'][0]['paths']

        # Choose a random server
        path = random.choice(paths)

        # Construct player and clip urls
        player_url = 'rtmp://%s/%s' % (path['address'], path['application'])
        clip_url = '%s/%s' % (path['path'], path['filename'])
        #Log('Player url: %s, clip url: %s' % (player_url, clip_url))

        return player_url, clip_url
    else:
        return [None, None]

def get_thumb(url):
    if url:
        try:
            image = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
            return DataObject(image, 'image/jpeg')
        except:
            pass

    return Redirect(R(ICON))
