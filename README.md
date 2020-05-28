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
    $ python subrake -u youtube.com

Options:
   optional arguments:
  -h, --help  show this help message and exit
  -u U        URL of the website to scan.
```
