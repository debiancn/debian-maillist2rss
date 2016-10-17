#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import PyRSS2Gen
import bs4
#import cgi
import requests
import email.utils # Py3.3+

MAILLIST_PAGEURL = "https://lists.debian.org/debian-devel-changes/recent"

def getUpdateDate(url: str) -> datetime.datetime:
    """
    get release datetime from url link.
    """
    #print('D: the url is' + url)
    local_r = requests.get(url)
    local_soup = bs4.BeautifulSoup(local_r.content, "html.parser")
    #print('D: the resp is' + str(local_soup))
    correct_list = [ x for x in local_soup.ul.find_all('li') if x.find_all('em') != [] and x.em.text == 'Date' ]
    #print('D: the list is'+str(correct_list), file=sys.stderr)
    datetime_rfc2822 = correct_list[0].text.split('Date: ')[1]
    return email.utils.parsedate_to_datetime(datetime_rfc2822)

if __name__ == "__main__":
    # CGI Headers
    print("Content-Type: application/rss+xml; charset=utf-8\r\n",end="")
    print("\r\n", end="")
    r = requests.get(MAILLIST_PAGEURL)
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    rssitems = []
    for i in soup.find_all('li'):
        # li for all the items
        if 'experimental' in i.a.text:
            continue
        local_link = r.url.rsplit('/', maxsplit=1)[0] + '/' + i.a.attrs['href']
        rssitems.append(
                PyRSS2Gen.RSSItem(
                    title = i.a.text.split('Accepted ')[1].split(' (')[0],
                    link = local_link,
                    description = i.a.text,
                    guid = i.a.attrs['name'],
                    pubDate = getUpdateDate(local_link),
                    )
                )
        print('.', file=sys.stderr)

    rss = PyRSS2Gen.RSS2(
            title = "Debian Unstable Updates",
            link = "https://lists.debian.org/debian-devel-changes/recent",
            description = "Latest package updates for Debian unstable",
            lastBuildDate = datetime.datetime.now(),
            items = rssitems,
            )
    print(rss.to_xml(encoding='UTF-8'))
