# !/usr/bin/python
# coding: utf-8

import urllib2  # get pages
# from fake_useragent import UserAgent # change user agent
import time  # to respect page rules
from bs4 import BeautifulSoup as BS
import pprint
import json
import io
from os import listdir, makedirs
from os.path import isfile, join, exists
import html5lib # needed for (very) lenient parsing
import re

__author__ = 'Arne Binder'


class ProconScraper(object):
    def __init__(self, rootUrl, outFolder):
        self.rootUrl = rootUrl  # like "https://www.openpetition.de"
        self.outFolder = outFolder
        # create output folder if necessary
        if not exists(outFolder):
            makedirs(outFolder)

def getQuestionID(petitionID):
    petitionPage = requestPage("http://" + petitionID + ".procon.org")

    soup = BS(petitionPage.decode('utf-8', 'ignore'), "html5lib")

    expr = re.compile(petitionID + "\.procon\.org/view\.answers\.php\?questionID=(\d+)")
    aLink = soup.find(href=expr)
    return expr.search(aLink['href']).group(1)

def getArguments(issueID):
    questionID = getQuestionID(issueID)
    return extractArguments(
        "http://" + issueID + ".procon.org/view.answers.reader-comments.php?questionID=" + questionID)

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

def extractArguments(url):
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

def extractIssueURLs():
    mainURL = "http://www.procon.org/debate-topics.php"
    page = requestPage(mainURL)
    soup = BS(page.decode('utf-8', 'ignore'), "html5lib")
    # aList = soup.select('')
    # expr = re.compile("http://([^\.]+)\.procon\.org/view\.answers\.php\?questionID=(\d+)")
    expr = re.compile("([^\.]+)\.procon\.org/view\.answers\.php\?questionID=(\d+)")
    aLinkList = soup.find_all(href=expr)

    result = []
    for a in aLinkList:
        m = expr.search(a['href'])
        result.append("http://" + m.group(1) + ".procon.org/view.answers.reader-comments.php?questionID=" + m.group(2))

    # aList1Refs = [a['href'] for a in aLinkList]

    # aList2 = [a for a in soup("a") if a.text == "Top Pro & Con Quotes"]
    # aList2Refs = [a['href'] for a in aList2]
    return result

    # http://undergod.procon.org/view.answers.php?questionID=1330

def main():
    # f = ProconScraper("procon.org", "out")

    # args = getArguments("climatechange")

    args = []
    # commentPageUrl = f.getArgumentPageUrl("climatechange")
    # args = getArguments(commentPageUrl)


    # print "as"
    # f.processSections(["in_zeichnung", "in_bearbeitung", "erfolg", "beendet", "misserfolg", "gesperrt"])

    pp = pprint.PrettyPrinter(indent=4)
    # id = "sind-vaeter-die-besseren-muetter-das-wechselmodell-als-standard-in-deutschland"
    # ids = f.extractAllPetitionIDs("in_zeichnung")
    # data = f.extractPartitionData(id)
    pp.pprint(extractIssueURLs())
    # writeJsonData(data, "test")


if __name__ == "__main__":
    main()