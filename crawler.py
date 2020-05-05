import sys

from canonicalizer import canonicalize
from get_next_url import get_next_urls
from get_text import get_text, filtertag
from check_url import check_media, check_response, check_robot

from bs4 import BeautifulSoup
import heapq
from collections import defaultdict
import time
import re
from glob import glob

from urllib import request
from urllib import parse
from urllib import robotparser

import requests

sys.setrecursionlimit(1000000)


def get_initial_url():
    seedlist = list()
    openfile = open('seedfile.txt', 'r')
    itr = 0
    for line in openfile:
        line = line.strip()
        line = canonicalize(line)
        seedlist.append((itr, line, None))
        itr += 1
    openfile.close()
    return seedlist

def dump_url_crawled(url_crawled):
    url_crawledfile = open('./info/urlcrawled.txt', 'w', encoding = 'utf-8')
    for url in url_crawled:
        url_crawledfile.write(url + "\n")
    url_crawledfile.close()

def dump_inlink(inlink):
    inlinkfile = open('./info/inlinks.txt', 'w', encoding = 'utf-8')
    for link in inlink:
        links = inlink[link]
        inlinkstr = ""
        for each in links:
            inlinkstr = inlinkstr + "\t" + each
        inlinkfile.write(link + "\t" + inlinkstr.strip() + "\n")
    inlinkfile.close()

def dump_outlink(outlink):
    outlinkfile = open('./info/outlinks.txt', 'w', encoding = 'utf-8')
    for link in outlink:
        links = outlink[link]
        outlinkstr = ""
        for each in links:
            outlinkstr = outlinkstr + "\t" + each
        outlinkfile.write(link + "\t" + outlinkstr.strip() + "\n")
    outlinkfile.close()

def dump_frontier(frontier):
    frontierfile = open('./info/frontiers.txt', 'w', encoding = 'utf-8')
    for priority, url, parent in frontier:
        frontierfile.write(str(priority) + "\t" + str(url) + "\t" + str(parent) + "\n")
    frontierfile.close()


def dump_content(outlink, url_response):
    fname = (len(glob('./page_content/*')))
    filename = './page_content/' + str(fname) + ".txt"
    web_content = open(filename, 'w', encoding = 'utf-8')
    for link in outlink:
        links = outlink[link]
        outlinkstr = ""
        head = ""
        html = ""
        text = ""
        header = ""
        if link in url_response:
            response = url_response[link]
        else:
            try:
                restriction = {"Accept-Language": "en-US,en;q=0.5"}
                response = requests.get(link, headers=restriction, timeout=5)
            except Exception as ex:
                continue
        web_content.write('<DOC>' + "\n")
        web_content.write('<DOCNO>' + link + '</DOCNO>' + "\n")
        try:
            soupobj = BeautifulSoup(response.text, features='lxml')
        except Exception as ex:
            continue
        header = str(response.headers)
        if soupobj:
            if soupobj.title:
                head = soupobj.title.text.strip()
            elif soupobj.head:
                head = soupobj.head.text.strip()
            text = get_text(soupobj.findAll(text=True))
            try:
                html = str(soupobj)
            except Exception as ex:
                print('Fail to dump' + link)
                continue
        web_content.write('<HEAD>' + head + '</HEAD>' + "\n")
        web_content.write('<HTTP-HEADER>' + header + '</HTTP-HEADER>' + "\n")
        web_content.write('<TEXT>' + text + '</TEXT>' + "\n")
        web_content.write('<RAW-HTML>' + html + '</RAW-HTML>' + "\n")
        for each in links:
            outlinkstr = outlinkstr + "\t" + each
        web_content.write('<OUTLINKS>' + outlinkstr.strip() + '</OUTLINKS>\n')
        web_content.write('</DOC>' + "\n")
    web_content.close()
    outlink.clear()
    url_response.clear()


def crawl_next(inlink, frontier, time_record, url_crawled, outlink, url_response):
    next_frontier = set()
    frontier_size = len(frontier)
    url_crawled_this_wave = set()
    while frontier:
        try:
            (priority, url, parent) = heapq.heappop(frontier)
        except Exception as ex:
            continue

        # 1. Check if this is a good url, if not, skip
        if url in url_crawled:
            if url in url_crawled_this_wave:
                inlink[url].append(parent)
            continue

        if check_media(url):
            continue
        try:
            # response = request.urlopen(url, timeout=5)
            restriction = {"Accept-Language": "en-US,en;q=0.5"}
            response = requests.get(url, headers=restriction ,timeout=5)
            url_component = parse.urlparse(url)
        except Exception as ex:
            continue
        domain = url_component.netloc.lower()
        scheme = url_component.scheme.lower()
        if domain.split('.')[1] == 'wikipedia' and domain.split('.')[0] != 'en':
            continue
        if len( domain.split('.') ) > 2:
            if domain.split('.')[2] == 'gov':
                continue
        if not check_robot(scheme, domain, url):
            continue
        if not check_response(response):
            continue
        print("Crawled: " + str(len(url_crawled)) + " URL. Currently on: " + url)
        
        # 2. Get the next urls
        # next_urls = get_next_urls(url, response)
        if domain not in time_record:
            time_record[domain] = time.time()
            next_urls = get_next_urls(url, response)
        else:
            if (time.time() - time_record[domain]) < 1:
                print("Sleep for" + str((time.time() - time_record[domain])))
                time.sleep(time.time() - time_record[domain])
                next_urls = get_next_urls(url, response)
            else:
                time_record[domain] = time.time()
                next_urls = get_next_urls(url, response)

        # 3. Saving information of the urls
        url_response[url] = response
        url_crawled.add(url)
        if parent != None:
            inlink[url].append(parent)
        else:
            if url in inlink:
                pass
            else:
                inlink[url] = []
        for next_url in next_urls:
            next_frontier.add((next_url, url))
            if next_url in url_crawled:
                if str(url) != str(next_url):
                    inlink[next_url].append(url)
        next_urls = list(next_urls)
        outlink[url] = next_urls

        # 4. Dump the web content when necessary.
        if (len(url_crawled) % 10) == 0:
            dump_inlink(inlink)
            dump_url_crawled(url_crawled)
            dump_frontier(frontier)
            dump_content(outlink, url_response)
        # Only process top 60% scored urls.
        if (len(frontier) / frontier_size) < 0.4 and len(frontier) > 6:
            break
        
        # 5. Stop and exit when we crawled enough urls.
        if len(url_crawled) >= 40300:
            dump_inlink(inlink)
            print("Finish crawling")
            exit()
    return next_frontier


def prepare_frontier(next_frontier, inlink):
    occurrence = {}
    restored_frontier = list()
    frontier_size = len(next_frontier)
    for link, parent in next_frontier:
        comp = parse.urlparse(link)
        domain = comp.netloc.lower()
        if domain in occurrence:
            occurrence[domain] += 1
        else:
            occurrence[domain] = 1
    for link, parent in next_frontier:
        comp = parse.urlparse(link)
        domain = comp.netloc.lower()
        rarity = occurrence[domain] / frontier_size
        if ( link in inlink ) and ( len(inlink[link]) > 0 ):
            score = float(1 * rarity) / len(inlink[link])
        else:
            score = float(1 * rarity)
        restored_frontier.append((score, link, parent))
    heapq.heapify(restored_frontier)
    return restored_frontier


def start_crawl():
    inlink = defaultdict(list)
    outlink = defaultdict(list)
    url_response = defaultdict()
    frontier = get_initial_url()
    for priority, url, parent in frontier:
        inlink[url] = []
    time_record = {}
    url_crawled = set()
    while True:
        next_frontier = crawl_next(inlink, frontier, time_record, url_crawled, outlink, url_response)
        frontier = prepare_frontier(next_frontier, inlink)



def restart_crawl():
    inlink = defaultdict(list)
    inlinkfile = open('./info/inlinks.txt', 'r',encoding='utf8')
    for line in inlinkfile:
        a = line.split()
        if len(a) == 1:
            inlink[a[0]] = []
        else:
            for i in range(1, len(a)):
                inlink[a[0]].append(a[i])
    outlink = defaultdict(list)
    frontier = []
    frontier_file = open('./info/frontiers.txt', 'r', encoding='utf8')
    for line in frontier_file:
        try:
            priority = float(line.split()[0])
        except Exception as ex:
            continue
        url = line.split()[1]
        if len( line.split() ) > 2:
            parent = line.split()[2]
            frontier.append((priority, url, parent))
        else:
            frontier.append((priority, url, None))
            if url in inlink:
                pass
            else:
                inlink[url] = []
    heapq.heapify(frontier)
    time_record = {}
    url_response = defaultdict()
    url_crawled = set()
    url_crawled_file = open('./info/urlcrawled.txt', 'r')
    for line in url_crawled_file:
        old_url_crawled = line.strip()
        url_crawled.add(old_url_crawled)
    while True:
        next_frontier = crawl_next(inlink, frontier, time_record, url_crawled, outlink, url_response)
        frontier = prepare_frontier(next_frontier, inlink)


def main(command: str):
    if command == "start":
        start_crawl()
    elif command == "restart":
        restart_crawl()

if __name__ == '__main__':
    if ( len(sys.argv) != 2 ) or ( sys.argv[1] != "start" and sys.argv[1] != "restart" ):
        print("\nUsage:\n  python crawler.py <command>\n")
        print("Commands:\n  start\t\tStart the crawler.\n  restart\tResume crawling from last break point.")
        print("")
        exit()
    command = sys.argv[1]
    main(command)
