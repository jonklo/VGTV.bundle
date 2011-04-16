# -*- coding: utf-8 -*-
from vgtv import *

VGTV_PREFIX = '/video/vgtv'

ART = 'art-default.jpg'
ICON = 'icon-default.png'


def Start():
    """
    Initiates the plugin.
    """
    Plugin.AddPrefixHandler(VGTV_PREFIX, MainMenu, 'VGTV', ICON, ART)
    
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    
    # Set defaults
    MediaContainer.content = 'Items'
    MediaContainer.art = R(ART)
    MediaContainer.title1 = 'VGTV'
    MediaContainer.viewGroup = 'List'
    DirectoryItem.thumb = R(ICON)



def MainMenu():
    """
    Sets up the main menu. All the menu functions are in separate files.
    """
    dir = MediaContainer()
    
    dir.Append(Function(DirectoryItem(CategoriesMenu, title='Alle kategorier')))
    dir.Append(Function(DirectoryItem(MostViewedMenu, title='Mest sett')))
    dir.Append(Function(DirectoryItem(RecentlyAddedMenu, title='Siste videoer')))
    
    return dir
