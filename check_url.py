import re
from urllib import robotparser

def check_media(url):
    extension = url[-4:].lower()
    if extension == '.jpg' or extension == '.png' or extension == '.gif' \
        or extension == '.svg' or extension == '.pdf' or extension == '.doc' \
        or extension == '.ppt' or extension == '.mp3' or extension == '.mp4' \
        or extension == '.zip' or extension == '.aac' or extension == '.wav' \
        or extension == '.wma' or extension == '.bmp' or extension == '.avi' \
        or extension == '.mkv' or extension == '.mov' or extension == '.flv' \
        or extension == '.xls' or extension == '.rtf' or extension == '-mp3':
        return True
    extension = url[-5:].lower()
    if extension == '.jpeg' or extension == '.tiff' or extension == '.pptx' \
        or extension == '.docs' or extension == '.xlsx' or extension == '.webm' \
        or extension == '.djvu':
        return True
    return False

def check_response(response):
    flag_type = False
    flag_lang = False
    if 'Content-Type' in response.headers:
        content_type = response.headers['Content-Type']
    else:
        return False
    if content_type is None or re.match('html|text', content_type):
        flag_type = True
    if flag_type:
        return True
    else:
        return False

def check_robot(scheme, domain, url):
    rp = robotparser.RobotFileParser()
    rp.set_url(scheme + "://" + domain + "/robots.txt")
    try:
        rp.read()
    except:
        return False
    return rp.can_fetch('*', url)

def test():
    pass

if __name__ == '__main__':
    test()
