# !/usr/bin/python
# coding: utf-8

import urllib2  # get pages
# from fake_useragent import UserAgent # change user agent
import time  # to respect page rules
from bs4 import BeautifulSoup as BS
# import pprint
import json
import io
from os import listdir, makedirs
from os.path import isfile, join, exists
import html5lib # needed for (very) lenient parsing

__author__ = 'Arne Binder'


class ProconScraper(object):
    def __init__(self, rootUrl, outFolder):
        self.rootUrl = rootUrl  # like "https://www.openpetition.de"
        self.outFolder = outFolder
        # create output folder if necessary
        if not exists(outFolder):
            makedirs(outFolder)

    def getArgumentPageUrl(self, petitionID):
        petitionPage = requestPage("http://" + petitionID + "." + self.rootUrl)

        soup = BS(petitionPage.decode('utf-8', 'ignore'), "html5lib")
        aList = soup.select('td#introtext > div > table > tbody > tr > td > table > tbody > tr > td > a')
        url = filter(lambda x: x.text == "Comments", aList)[0]['href']
        return url

def requestPage(url):
    request = urllib2.Request(url, None, {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'})
    try:
        print 'request ' + url
        document = urllib2.urlopen(request).read()
    except urllib2.HTTPError, err:
        if err.code == 503:
            print "################################################# 503 #################################################"
            time.sleep(30)
            document = request(url)
        else:
            raise
    return document

def getArguments(url):
    page = requestPage(url)
    soup = BS(page.decode('utf-8', 'ignore'), "html5lib")
    proArgList = soup.select('div#comments-container > div.pro > ul.comments > li.comment')
    conArgList = soup.select('div#comments-container > div.con > ul.comments > li.comment')
    return {'pro': [extractArgumentData(arg) for arg in proArgList], 'con': [extractArgumentData(arg) for arg in conArgList]}

def extractArgumentData(argElem):
    result = {'content': argElem.select('div.contents > blockquote')[0].text}
    replies = argElem.select('div.reply-replies > ul.replies > li.reply')
    result['replies'] = [reply.select('div.contents > blockquote')[0].text for reply in replies]
    return result


def main():
    f = ProconScraper("procon.org", "out")
    commentPageUrl = f.getArgumentPageUrl("medicalmarijuana")
    args = getArguments(commentPageUrl)
    print "as"
    # f.processSections(["in_zeichnung", "in_bearbeitung", "erfolg", "beendet", "misserfolg", "gesperrt"])

    # pp = pprint.PrettyPrinter(indent=4)
    # id = "sind-vaeter-die-besseren-muetter-das-wechselmodell-als-standard-in-deutschland"
    # ids = f.extractAllPetitionIDs("in_zeichnung")
    # data = f.extractPartitionData(id)
    # pp.pprint(ids)
    # writeJsonData(data, "test")


if __name__ == "__main__":
    main()