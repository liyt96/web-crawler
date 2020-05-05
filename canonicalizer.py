from urllib import parse
import posixpath

'''
Convert the scheme and host to lower case: 
HTTP://www.Example.com/SomeFile.html → http://www.example.com/SomeFile.html

Remove port 80 from http URLs, and port 443 from HTTPS URLs, keep non-default port:
http://www.example.com:80 → http://www.example.com
http://www.example.com:8080 → http://www.example.com:8080

Make relative URLs absolute: 
if you crawl http://www.example.com/a/b.html and find the URL ../c.html, 
it should canonicalize to http://www.example.com/a/c.html.

Remove the fragment, which begins with #: 
http://www.example.com/a.html#anything → http://www.example.com/a.html

Remove parameters


Remove duplicate slashes: 
http://www.example.com//a.html → http://www.example.com/a.html

Remove default index pages:
http://www.example.com/index.html → http://www.example.com

More Reference: https://en.wikipedia.org/wiki/URI_normalization
'''

# todo, remove parameters

def canonicalize(url, parent_url=None):
    '''
    Canonicalize URLs following the 5 rules above.
    :param url: URL to be canonicalized
    :param parent_url: parent URL, parameter for converting relative URLS to absolute
    :return: canonicalized URL
    '''

    # scheme='http', netloc='www.example.com', path='/SomeFile.html', params='', query='', fragment=''
    url_tuple = parse.urlparse(url)
    # print(url_tuple)
    (scheme, netloc, path, parameters, query, fragment) = url_tuple

    # convert scheme to lower case
    if scheme == '':   # e.g., //www.example.com, scheme = '', netloc = 'www.example.com'
        scheme = 'http'
    scheme = scheme.lower()

    if netloc == '':    # relative path
        if parent_url is None:
            raise ValueError('Cannot resolve relative url without parent url')
        parent_url_tuple = parse.urlparse(parent_url)
        scheme = parent_url_tuple.scheme
        netloc = parent_url_tuple.netloc

        if path.startswith('/'):
            path = path
        else:
            parent_path = parent_url_tuple.path
            last_slash_index = parent_path.rfind('/')
            parent_path_dir = parent_path[: last_slash_index]
            path = parent_path_dir + '/' + path

    # remove default port from netloc, keep non-default port
    userinfo = get_userinfo(netloc)
    hostname = get_hostname(netloc)
    port = get_port(netloc)

    netloc = '{}@{}'.format(userinfo, hostname) if userinfo is not None else hostname
    if port is not None:
        if (scheme == 'http' and port != 80) or (scheme == 'https' and port != 443):
            netloc = '{}:{}'.format(netloc, port)

    # clean path
    # remove default index page
    if path.lower() == '/index.htm' or path.lower() == '/index.html' \
            or path.lower() == '/index.asp' or path.lower() == '/index.aspx':
        path = ''

    # remove duplicate slashes
    # remove . and ..
    # '/' for empty path
    # POSIX allows one or two initial slashes, but treats three or more as single slash
    path = posixpath.normpath(path)
    path = '' if path == '.' else path.replace('//', '/')

    # todo, maybe remove parameters
    # set fragment to '' to remove #
    new_url_tuple = (scheme, netloc, path, parameters, query, '')
    # new_url_tuple = (scheme, netloc, path, '', '', '')
    return parse.urlunparse(new_url_tuple)


'''
Additional attributes that provide access to parsed-out portions of the netloc.
'''
def get_username(netloc):
    if '@' in netloc:
        userinfo = netloc.split('@', 1)[0]
        if ':' in userinfo:
            username = userinfo.split(':', 1)[0]
        return username
    return None


def get_password(netloc):
    if '@' in netloc:
        userinfo = netloc.split('@', 1)[0]
        if ':' in userinfo:
            return userinfo.split(':', 1)[1]
    return None


def get_userinfo(netloc):
    if '@' in netloc:
        return netloc.split('@', 1)[0]
    return None


def get_port(netloc):
    if '@' in netloc:
        netloc = netloc.split('@', 1)[1]
    if ':' in netloc:
        port = netloc.split(':', 1)[1]
        try:
            port_int = int(port, 10)
        except Exception as ex:
            return None
        return port_int
    return None


def get_hostname(netloc):
    if '@' in netloc:
        netloc = netloc.split('@', 1)[1]
    if ':' in netloc:
        netloc = netloc.split(':', 1)[0]
    return netloc.lower() or None


if __name__ == '__main__':
    # # Convert the scheme and host to lower case
    # print(canonicalize('HTTP://www.EXAMPLE.com/SomeFile.html', 'http://www.example.com/a/b.html'))
    # # Remove port 80 from http URLs, and port 443 from HTTPS URLs, keep non-default port
    # print(canonicalize('http://www.example.com:80', 'http://www.example.com/a/b.html'))
    # print(canonicalize('https://www.example.com:443', 'http://www.example.com/a/b.html'))
    # print(canonicalize('https://www.example.com:6000', 'http://www.example.com/a/b.html'))
    # # Make relative URLs absolute
    # print(canonicalize('../c.html', 'http://www.example.com/a/b.html'))
    # print(canonicalize('../c.html', 'HttP://www.EXAMPLE.com/a/b/d/e.html'))
    # print(canonicalize('../../c.html', 'http://www.example.com/a/b/d/e.html'))
    # print(canonicalize('../c.html', 'http://www.example.com/a/b/d/..e.html'))
    # print(canonicalize("../../../c.html", 'http://www.example.com/a/b/d/e.html'))
    # print(canonicalize('/wiki/Doctrine', 'https://en.wikipedia.org/wiki/Sino-Soviet_split'))
    # # Remove the fragment, which begins with #
    # print(canonicalize('http://www.example.com/a.html#anything', 'http://www.example.com/a/b.html'))
    # # # todo, Remove parameters
    # # print(canonicalize('https://majestic.com/reports/majestic-million?majesticMillionType=2&tld=&oq=', 'https://majestic.com/reports/majestic-million'))
    # # # Remove duplicate slashes
    # print(canonicalize('http://www.example.com//a//b////c.html', 'http://www.example.com/a/b.html'))
    # # Remove . and ..
    # print(canonicalize('http://www.example.com/a/./b/../c.html', 'http://www.example.com/a/b.html'))
    # # Remove default index pages
    # print(canonicalize('http://www.example.com/index.html', 'http://www.example.com/a/b.html'))


    # # Convert the scheme and host to lower case
    # assert(canonicalize('HTTP://www.EXAMPLE.com/SomeFile.html', 'http://www.example.com/a/b.html') == 'http://www.example.com/SomeFile.html')
    # # Remove port 80 from http URLs, and port 443 from HTTPS URLs, keep non-default port
    # assert(canonicalize('http://www.example.com:80', 'http://www.example.com/a/b.html') == 'http://www.example.com')
    # assert(canonicalize('https://www.example.com:443', 'http://www.example.com/a/b.html') == 'https://www.example.com')
    # assert(canonicalize('https://www.example.com:6000', 'http://www.example.com/a/b.html') == 'https://www.example.com:6000')
    # # Make relative URLs absolute
    # assert(canonicalize('../c.html', 'http://www.example.com/a/b.html') == 'http://www.example.com/c.html')
    # assert(canonicalize('../c.html', 'HttP://www.EXAMPLE.com/a/b/d/e.html') == 'http://www.example.com/a/b/c.html')
    # assert(canonicalize('../../c.html', 'HttP://www.EXAMPLE.com/a/b/d/e.html') == 'http://www.example.com/a/c.html')
    # assert(canonicalize("../../../c.html", 'http://www.example.com/a/b/d/e.html') == 'http://www.example.com/c.html')
    # assert(canonicalize('/wiki/Doctrine', 'https://en.wikipedia.org/wiki/Sino-Soviet_split') == 'https://en.wikipedia.org/wiki/Doctrine')
    # # Remove the fragment, which begins with #
    # assert(canonicalize('http://www.example.com/a.html#anything', 'http://www.example.com/a/b.html') == 'http://www.example.com/a.html')
    # # # todo, Remove parameters
    # # assert(canonicalize('https://majestic.com/reports/majestic-million?majesticMillionType=2&tld=&oq=', 'https://majestic.com/reports/majestic-million') == 'https://majestic.com/reports/majestic-million')
    # # # Remove duplicate slashes
    # assert(canonicalize('http://www.example.com//a//b////c.html', 'http://www.example.com/a/b.html') == 'http://www.example.com/a/b/c.html')
    # # Remove . and ..
    # assert(canonicalize('http://www.example.com/a/./b/../c.html', 'http://www.example.com/a/b.html') == 'http://www.example.com/a/c.html')
    # # Remove default index pages
    # assert(canonicalize('http://www.example.com/index.html', 'http://www.example.com/a/b.html') == 'http://www.example.com')



    # # url1 = "/wiki/Corrective_Movement_(Syria)"
    # # url_tuple1 = parse.urlparse(url1)
    # # print(url_tuple1)
    # #
    # # url2 = "/wiki/1973_Afghan_coup_d%27%C3%A9tat"
    # # url_tuple2 = parse.urlparse(url2)
    # # print(url_tuple2)

    # url = '#mw-head'
    # url_tuple = parse.urlparse(url)
    # print(url_tuple)
    # print(canonicalize('http://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=D99E98D76B7FD1FACBAD151408D16406?doi=10.1.1.374.2005&rep=rep1&type=pdf'))
    pass
