# -*- coding: utf-8 -*-
from util import fix_chars

BASE_URL_FEED = 'http://www.vgtv.no/api/'
PLAYLIST_NAMESPACE = {'ns1': 'http://xspf.org/ns/0/'}
CACHE_HTML_INTERVAL = 3600 * 5


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
            Log(cat)
            dir.Append(Function(DirectoryItem(VideoListMenu, title=cat['title']), id=cat['id']))
        return dir
    
    
    # Fetch all top level categories
    url = '%s?do=feed&action=categories' % BASE_URL_FEED
    rss = HTML.ElementFromURL(url, cacheTime=CACHE_HTML_INTERVAL, encoding='utf-8')
    categories = rss.xpath('//channel/categories/item')
    
    # Display error message if no categories are found
    if not len(categories):
        return (MessageContainer(header=L('title'), message=L('podcast_noepisodes'), title1=L('title')))
        
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
    rss = HTML.ElementFromURL(url, cacheTime=CACHE_HTML_INTERVAL, encoding='utf-8')
    
    videos = rss.xpath('//channel/item')
    
    # Display error message if no categories are found
    if not len(videos):
        return (MessageContainer(header=L('title'), message=L('noepisodes'), title1=L('title')))
        
    for item in videos:
        title = item.xpath('./title/text()')[0]
        clip_id = item.xpath('./id/text()')[0]
        
        try:
            img_url = item.xpath('./enclosure')[0].get('url')
        except:
            img_url = None
        
        try:
            desc = item.xpath('./description/text()')[0]
        except:
            desc = None
        
        player_url, clip_url = get_player_and_clip_url(clip_id)
        
        dir.Append(RTMPVideoItem(url=player_url, clip=clip_url, title=title, summary=desc, thumb=img_url))
    
    return dir


###########
# Helpers #
###########

def get_player_and_clip_url(id):
    """
    Fetches and separates the player and clip urls.
    """
    url = '%s?do=playlist&id=%s' % (BASE_URL_FEED, id)
    rss = XML.ElementFromURL(url, cacheTime=CACHE_HTML_INTERVAL, encoding='utf-8')
    
    try:
        locations = rss.xpath('//ns1:track', namespaces=PLAYLIST_NAMESPACE)[0]
        location = locations.xpath('./ns1:location/text()', namespaces=PLAYLIST_NAMESPACE)[0]
    
        # Extract the player and clip urls
        player_url, clip_url = '/'.join(location.split('/')[0:4]), '/'.join(location.split('/')[4:])
        Log('Player url: %s, clip url: %s' % (player_url, clip_url))
        
    except:
        player_url, clip_url = None, None
        Log('ERROR: could not fetch clip url for ID: %s' % id)
    
    return player_url, clip_url
    