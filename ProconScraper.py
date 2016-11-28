# !/usr/bin/python
# coding: utf-8

import urllib2  # get pages
import time  # to respect page rules
from bs4 import BeautifulSoup as BS
import json
import io
from os import makedirs
from os.path import join, exists
import html5lib  # needed for (very) lenient parsing
import re

__author__ = 'Arne Binder'


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


def extractArguments((url, debateID)):
    page = requestPage(url)
    soup = BS(page.decode('utf-8', 'ignore'), "html5lib")

    searchUrl = 'http://'+debateID+'\.procon\.org/?'
    question = soup.find("a", href=re.compile(searchUrl), title=re.compile(".*"))['title']

    '''
    # extract question and topic from title and meta description
    title = soup.select('html > head > title')[0].text
    contentDesc = soup.select('html > head > meta[name=description]')[0]['content']
    titleSuffix = u' - Reader Comments - ProCon.org'
    contentDescSuffix = u' Read pros, cons, and expert responses in the debate.'
    if title[-len(titleSuffix):] == titleSuffix and contentDesc[-len(contentDescSuffix):] == contentDescSuffix:
        title = title[:-len(titleSuffix)]
        contentDesc = contentDesc[:-len(contentDescSuffix)]
        topic = title[len(contentDesc) + 3:]
    else:
        raise Exception(
            'The title = "' + title + '" does not end with the expected title suffix = "' + titleSuffix
            + '" or the content description = "' + contentDesc
            + '" does not end with the expected content description suffix = "' + contentDescSuffix + '"')
    '''

    proArgList = soup.select('div#comments-container > div.pro > ul.comments > li.comment')
    conArgList = soup.select('div#comments-container > div.con > ul.comments > li.comment')
    m = re.search('http://([^^.]+)', url)

    return {'id': m.group(1), 'question': question,
            'pro': [extractArgument(arg) for arg in proArgList],
            'con': [extractArgument(arg) for arg in conArgList]}


def extractArgument(argElem):
    result = extractArgumentData(argElem)
    replies = argElem.select('div.reply-replies > ul.replies > li.reply')
    result['replies'] = [extractArgumentData(reply) for reply in replies]
    return result

def extractArgumentData(argElem):
    result = {}
    result['content'] = argElem.select('div.contents > blockquote')[0].text
    result['votesUp'] = argElem.select('div.contents > div.info > span.votes-up > a.votes-up')[0].text
    result['votesDown'] = argElem.select('div.contents > div.info > span.votes-down > a.votes-down')[0].text
    result['votesUp'] = result['votesUp'][1:]
    result['votesDown'] = result['votesDown'][1:]
    return result


def extractIssueURLs():
    mainURL = "http://www.procon.org/debate-topics.php"
    page = requestPage(mainURL)
    soup = BS(page.decode('utf-8', 'ignore'), "html5lib")
    expr = re.compile("http://([^\.]+)\.procon\.org/view\.answers\.php\?questionID=(\d+)")
    aLinkList = soup.find_all(href=expr)

    result = []
    for a in aLinkList:
        m = expr.search(a['href'])
        result.append(("http://" + m.group(1) + ".procon.org/view.answers.reader-comments.php?questionID=" + m.group(2), m.group(1)))

    return result


def writeJsonData(data, path):
    with io.open(path + '.json', 'w', encoding='utf8') as json_file:
        out = json.dumps(data, ensure_ascii=False)
        # unicode(data) auto-decodes data to unicode if str
        json_file.write(unicode(out))


def main():
    # f = ProconScraper("procon.org", "out")
    outFolder = "out"

    if not exists(outFolder):
        makedirs(outFolder)

    urls = extractIssueURLs()

    failedUrls = []

    for url in urls:
        try:
            data = extractArguments(url)
            writeJsonData(data, join(outFolder, data['id']))
        except:
            failedUrls.append(url)

    writeJsonData(failedUrls, "FAILED")


if __name__ == "__main__":
    main()
