from bs4 import BeautifulSoup
from canonicalizer import canonicalize


def get_next_urls(url, response):
    next_urls_set = set()
    try:
        soupobj = BeautifulSoup(response.text, features='lxml')
    except Exception as ex:
        # print(ex)
        return next_urls_set
    if soupobj:
        for link in soupobj.find_all('a'):
            href = link.get('href')
            if href is None:
                continue
            else:
                next_url = href.strip()
                try: 
                    next_url = canonicalize(next_url, url)
                except Exception as ex:
                    continue
                if next_url:
                    next_urls_set.add(next_url)
    return next_urls_set


def test():
    pass

if __name__ == '__main__':
    test()
