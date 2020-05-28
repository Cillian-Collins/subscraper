<div align="center"><h1> 
    <img src="https://i.imgur.com/SfYw4T4.png"/> <br>    
    SUBSCRAPER
</h1>
<b>Reconnaissance tool which scans javascript files for subdomains and then iterates over all javascript files hosted on subsequent subdomains to enumerate a list of subdomains for a given URL.</b>
</div>

## Features

* Scans a domain and identifies all subdomains in javascript files.
* Scans subdomains and identifies all subdomains in subsequent files.
* Continues until no new subdomains are identified.

## Install

To install you should first clone this repository and then open the command line in the cloned directory and run the install command below.

```
pip install -r requirements.txt
```

## Parameters

```
Syntax: 
    $ python subscraper.py -u youtube.com
    $ python subscraper.py -u youtube.com -o output.txt

Options:
  -h, --help  show this help message and exit
  -u U        URL of the website to scan.
  -o [O]      Output file (for results).
```

## Contributions

There's a lot of work left to do here, specifically relating to the whitelisting of which javascript files we scan and which we ignore. Generally speaking, for a domain ``youtube.com`` we would look to check any files which are relative ``script.js`` and ``/scripts/script.js``. We should also look to include all javascript files hosted on ``*.youtube.com`` and if possible, even include these subdomains in our output, assuming they are not already included in our output. This can often happen if CDNs are hosting javascript files so it's important not to miss anything.
