import requests
import argparse
import re
from bs4 import BeautifulSoup
from Color_Console import ctext

'''
Usage: argparse.py -u website.com -o output.txt
'''

parser = argparse.ArgumentParser(description='Extract subdomains from javascript files.')
parser.add_argument('-u', help='URL of the website to scan.', required=True)
parser.add_argument('-o', help='Output file (for results).', nargs="?")
args = parser.parse_args()

'''
We define subdomains enumerated and sites visited in order to compare both lists.
We can thus determine which subdomains have not yet been checked.
This 'domino effect' of subsequent requests yields much more subdomains than scanning only the front page.
Threading would be useful here for optimization purposes.
'''


SUBDOMAINS_ENUMERATED = []
SITES_VISITED = []


'''
Find scripts function will initiate the sequence by identifying all script tags on a given page.
From there it enumerates a list, sorts it for duplicates and then passes the script content to find_subdomains function.
'''


def find_scripts(url):
    # If we already checked the site, ignore it.
    if url in SITES_VISITED:
        return False
    # Otherwise, add it to list of sites which we have checked
    SITES_VISITED.append(url)
    r = is_live(url)
    if not r:
        return False
    soup = BeautifulSoup(r.text, 'lxml')
    script_tags = soup.find_all('script')
    for script_tag in script_tags:
        '''
        Here we need to account for relative URLs and many other types of CDNs.
        We should also take into account that files hosted on other websites can usually be omitted.
        As such we will omit these in order to prevent us falling into a rabbit hole of requests.
        There is a margin of error here but it's probably negligible in the bigger picture.
        '''
        if is_src(script_tag.attrs):
            find_scripts(re.search("[a-zA-Z0-9-_.]+\.[a-zA-Z]{2,}", script_tag.attrs['src']).group())
        else:
            find_subdomains(script_tag)


'''
Unfortunately to identify whether a script tag has a 'src' attribute or not we need to capture the exception.
There are several alternative solutions but making it into a function like below seems the most efficient.
'''


def is_src(tag):
    try:
        if tag['src']:
            return True
    except:
        return False


'''
Here we will use another function to capture errors in our requests.
It's very common for request errors so we simply ignore it.
'''


def is_live(url):
    try:
        r = requests.get('http://' + str(url))
        return r
    except:
        return False


'''
Once we have our list of javascript code, we must find all subdomains in the code.
As such, we compare it to a regex and then sort for the various exceptions one might expect to find.
'''


def find_subdomains(script):
    subdomain_regex = re.findall(r"[%\\]?[a-zA-Z0-9][a-zA-Z0-9-_.]*\." + args.u, str(script))
    for subdomain in subdomain_regex:
        if "%" in subdomain:
            # If the subdomain is preceded by URL encoding, we removed it.
            parsed_subdomain = subdomain.split("%")[-1][2:]
            if parsed_subdomain not in SUBDOMAINS_ENUMERATED:
                ctext(parsed_subdomain, "green", "black")
                SUBDOMAINS_ENUMERATED.append(parsed_subdomain)
        elif "\\x" in subdomain:
            # If the subdomain is preceded by \x escape sequence, remove it.
            parsed_subdomain = subdomain.split("\\x")[-1][2:]
            if parsed_subdomain not in SUBDOMAINS_ENUMERATED:
                ctext(parsed_subdomain, "green", "black")
                SUBDOMAINS_ENUMERATED.append(parsed_subdomain)
        else:
            # Otherwise proceed as normal.
            if subdomain not in SUBDOMAINS_ENUMERATED:
                ctext(subdomain, "green", "black")
                SUBDOMAINS_ENUMERATED.append(subdomain)

    '''
    If our total subdomains discovered is not the same length as our sites visited, scan the rest of our subdomains.
    '''
    if len(list(set(SUBDOMAINS_ENUMERATED))) != len(list(set(SITES_VISITED))):
        for site in SUBDOMAINS_ENUMERATED:
            find_scripts(site)


# Initiate user input
find_scripts(args.u)
if args.o:
    with open(args.o, "w") as f:
        f.write("".join(x + "\n" for x in SUBDOMAINS_ENUMERATED))
