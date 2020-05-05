from bs4 import BeautifulSoup

from urllib import request
from urllib import parse
from urllib import robotparser

import requests

import re

def filtertag(element):
    if element.parent.name in ['b', 'p']:
        return True


def get_text(texts):
    available_text = filter(filtertag, texts)
    txt = ''
    for t in available_text:
        txt = txt + str(t)
    txt = re.sub(' +', ' ', txt)
    return txt.strip()

if __name__ == '__main__':
    url = 'https://liyt96.github.io'
    headers = {"Accept-Language": "en;q=1"}
    response = requests.get(url, headers=headers, timeout=5)
    # response = requests.get('http://files.knihi.com/Knihi/Slounik/Bielaruskaja_encyklapedyja.djvu.zip/Bielaruskaja_encyklapedyja.08.djvu', timeout=5)
    # response = requests.get('http://www.ccs.neu.edu/home/vip/teach/IRcourse/1_retrieval_models/other_notes/zhai-lafferty.pdf', timeout=5)
    soupobj = BeautifulSoup(response.text, features="lxml")

    print( get_text ( soupobj.findAll(text=True) ) )
    print( soupobj.title.text.strip() )
    print( response.headers )