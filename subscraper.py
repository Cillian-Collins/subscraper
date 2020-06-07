#!/usr/bin/env python3
import argparse
import re
import requests
import urllib3

from bs4 import BeautifulSoup
from Color_Console import ctext


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Usage: argparse.py -u website.com -o output.txt

parser = argparse.ArgumentParser(description='Extract subdomains from javascript files.')
parser.add_argument('-u', help='URL of the website to scan.', required=True)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-o', help='Output file (for results).', nargs="?")
group.add_argument('-v', help='Enables verbosity', action="store_true")
args = parser.parse_args()

"""
We define subdomains enumerated and sites visited in order to compare both lists.
We can thus determine which subdomains have not yet been checked.
This 'domino effect' of subsequent requests yields much more subdomains than scanning only the front page.
Threading would be useful here for optimization purposes.
"""

SUBDOMAINS_ENUMERATED = []
SITES_VISITED = []
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}

"""
Find scripts function will initiate the sequence by identifying all script tags on a given page.
From there it enumerates a list, sorts it for duplicates and then passes the script content to find_subdomains function.
"""


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
        """
        Here we need to account for relative URLs and many other types of CDNs.
        We sh account that files hosted on other websites can usually be omitted.
        As such we will omit these in order to prevent us falling into a rabbit hole of requests.
        There is a margin of error here but it's probably negligible in the bigger picture.
        """
        if is_src(script_tag.attrs):
            script_src = script_tag.attrs['src']
            if script_src[0] == "/" and script_src[1] != "/":
                parsed_url = url + script_src
            elif script_src[0] == "/" and script_src[1] == "/":
                parsed_url = script_src[2:]
            elif "http" not in script_src:
                parsed_url = url + "/" + script_src
            else:
                parsed_url = re.search("[a-zA-Z0-9-_.]+\.[a-zA-Z]{2,}", script_src).group()
            try:
                find_subdomains(requests.get('http://' + parsed_url, verify=False, headers=HEADERS).text)
                src_url = re.search("[a-zA-Z0-9-_.]+\.[a-zA-Z]{2,}", script_src).group()
                if src_url not in SUBDOMAINS_ENUMERATED:
                    SUBDOMAINS_ENUMERATED.append(src_url)
            except:
                pass
        else:
            find_subdomains(script_tag)


def is_src(tag):
    """
    Checks if dictionary has key and verifies that it is a dictionary.
    """
    return isinstance(tag, dict) and 'src' in tag


def is_live(url):
    """
    Here we will use another function to capture errors in our requests.
    It's very common for request errors so we simply ignore it.
    """
    try:
        r = requests.get('http://' + str(url), verify=False, headers=HEADERS)
        return r
    except:
        return False


def find_subdomains(script):
    """
    Once we have our list of javascript code, we must find all subdomains in the code.
    As such, we compare it to a regex and then sort for the various exceptions one might expect to find.
    """
    subdomain_regex = re.findall(r"[%\\]?[a-zA-Z0-9][a-zA-Z0-9-_.]*\." + args.u, str(script))
    for subdomain in subdomain_regex:
        # If the subdomain is preceded by URL encoding, we removed it.
        if "%" in subdomain:
            # Sort for double URL encoding
            while "%25" in subdomain:
                subdomain = subdomain.replace("%25", "%")
            parsed_subdomain = subdomain.split("%")[-1][2:]
        # If the subdomain is preceded by \x escape sequence, remove it.
        elif "\\x" in subdomain:
            ctext("[+] " + subdomain, "red")
            parsed_subdomain = subdomain.split("\\x")[-1][2:]
        # If the subdomain is preceded by \u unicode sequence, remove it.
        elif "\\u" in subdomain:
            ctext("[+] " + subdomain, "red")
            parsed_subdomain = subdomain.split("\\u")[-1][4:]
        # Otherwise proceed as normal.
        else:
            parsed_subdomain = subdomain
        if parsed_subdomain not in SUBDOMAINS_ENUMERATED:
            if args.v:
                ctext("[+] " + subdomain, "green")
            SUBDOMAINS_ENUMERATED.append(subdomain)

    # If our total subdomains discovered is not the same length as our sites visited, scan the rest of our subdomains.
    if len(list(set(SUBDOMAINS_ENUMERATED))) != len(list(set(SITES_VISITED))):
        for site in SUBDOMAINS_ENUMERATED:
            find_scripts(site)


def ascii_banner():
    ctext("                      `. ___", "red")
    ctext("                    __,' __`.                _..----....____", "red")
    ctext("        __...--.'``;.   ,.   ;``--..__     .'    ,-._    _.-'", "red")
    ctext("  _..-''-------'   `'   `'   `'     O ``-''._   (,;') _,'", "red")
    ctext(",'________________                          \`-._`-','", "red")
    ctext(" `._              ```````````------...___   '-.._'-:", "red")
    ctext("    ```--.._      ,.                     ````--...__\-.", "red")
    ctext("            `.--. `-`                       ____    |  |`", "red")
    ctext("              `. `.                       ,'`````.  ;  ;`", "red")
    ctext("                `._`.        __________   `.      \'__/`", "red")
    ctext("                   `-:._____/______/___/____`.     \  `", "red")
    ctext("         SUBSCRAPER            |       `._    `.    \\", "red")
    ctext("         SUBSCRAPER            `._________`-.   `.   `.___", "red")
    ctext("         SUBSCRAPER                v1.0.0         `------'`", "red")
    ctext("\nSubdomains Found:\n")


def main():
    # Banner
    ascii_banner()
    # Suppress InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # Initiate user input
    find_scripts(args.u)
    if args.o:
        with open(args.o, "w") as f:
            f.write("".join(x + "\n" for x in SUBDOMAINS_ENUMERATED))


if __name__ == '__main__':
    main()
