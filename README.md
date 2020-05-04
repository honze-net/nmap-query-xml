# nmap-query-xml
A simple program to query nmap xml files in the terminal.
![screenshot 1](https://raw.githubusercontent.com/honze-net/nmap-query-xml/master/screenshot1.png)

## Prerequisites
You will need Python3 and python-libnmap: https://github.com/savon-noir/python-libnmap#install

## Installation
```
# Clone or download to your desired installation folder.
git clone https://github.com/honze-net/nmap-query-xml
# Make nmap-query-xml.py executable
chmod +x nmap-query-xml/nmap-query-xml.py
# Create a symbolic link in one of your $PATH folders. E. g.
sudo ln -s $(pwd)/nmap-query-xml/nmap-query-xml.py /usr/bin/nmap-query-xml
```

## Introduction
The easiest usage is to call `nmap-query-xml` just with a xml file as argument. This will list all services and hosts of all open ports like this:
```
$ nmap-query-xml scanme.xml
ssh://scanme.nmap.org:22
http://scanme.nmap.org:80
tcpwrapped://scanme.nmap.org:31337
ssh://scanme2.nmap.org:22
smtp://scanme2.nmap.org:25
http://scanme2.nmap.org:80
ssls://scanme2.nmap.org:443
```
(The scanme.xml was generated with: `nmap -sS -T4 -A -sC -oA scanme scanme.nmap.org scanme2.nmap.org`)

In the beginning of an assessment (bug bounty, pentest, etc.) you might want to create your project folder structure.
```
$ nmap-query-xml scanme.xml --pattern "mkdir -p ~/project/{ip}/{protocol}/{port}"
mkdir -p ~/project/45.33.32.156/tcp/22
mkdir -p ~/project/45.33.32.156/tcp/80
mkdir -p ~/project/45.33.32.156/tcp/31337
mkdir -p ~/project/45.33.49.119/tcp/22
mkdir -p ~/project/45.33.49.119/tcp/25
mkdir -p ~/project/45.33.49.119/tcp/80
mkdir -p ~/project/45.33.49.119/tcp/443
```
As you can see, every line is a valid `sh` command. So you can pipe this output to `sh` and it will create the project folder like this: 
```
$ tree project
project
├── 45.33.32.156
│   └── tcp
│       ├── 22
│       ├── 31337
│       └── 80
└── 45.33.49.119
    └── tcp
        ├── 22
        ├── 25
        ├── 443
        └── 80
```
The `--pattern` option is a string, which is printed for every (default: open) port discovered. The key is to use variables, which are listed below.

### List of variables used in --pattern

- {hostname} - The first hostname of a list of hostnames (nmap could have detected more via rDNS). If no hostname was detected, the IP will be used.
- {hostnames} - Comma separated list of all hostnames. If no hostname was detected, the IP will be used.
- {ip} - The IP address of the host. 
- {port} - The port number.
- {protocol} - The protocol used (mostly tcp or udp).
- {s} - This a flag for SSL/TLS tunnel usage. It is "s" if SSL/TLS is used and "" otherwise.
- {service} - The service name discovered by nmap. Sometimes https is discovered as http with the SSL/TLS flag. Use {service}{s} then.
- {state} - The port state nmap discovered (open, closed, filtered, etc.).
- {xmlfile} - The file name (supplied as argument). Great for searching a lot of xml files for a specific host for example.


If you want to add hostnames to your project, you could create symbolic links like this:

In your project folder run:
```
$ nmap-query-xml scanme.xml --pattern "ln -s {ip} {hostname}" | sort -u
ln -s 45.33.32.156 scanme.nmap.org
ln -s 45.33.49.119 scanme2.nmap.org
```
Note that I copied the scanme.xml in the project folder before. But you can store them anywhere, so you might have to adjust the path to the scanme.xml. The `sort -u` will remove duplicates from the query.

Now it will look like this:
```
$ tree
.
├── 45.33.32.156
│   └── tcp
│       ├── 22
│       ├── 31337
│       └── 80
├── 45.33.49.119
│   └── tcp
│       ├── 22
│       ├── 25
│       ├── 443
│       └── 80
├── scanme2.nmap.org -> 45.33.49.119
├── scanme.nmap.org -> 45.33.32.156
└── scanme.xml
```

Now you start your assessment! Want to curl each http host for a `robots.txt` and save it in your project folder?
```
$ nmap-query-xml scanme.xml --service http --pattern "curl -L -o ./{ip}/{protocol}/{port}/robots.txt {service}://{hostname}:{port}/robots.txt "
curl -L -o ./45.33.32.156/tcp/80/robots.txt http://scanme.nmap.org:80/robots.txt 
curl -L -o ./45.33.49.119/tcp/80/robots.txt http://scanme2.nmap.org:80/robots.txt
```
This will lead to:
```
$ tree
.
├── 45.33.32.156
│   └── tcp
│       ├── 22
│       ├── 31337
│       └── 80
│           └── robots.txt
├── 45.33.49.119
│   └── tcp
│       ├── 22
│       ├── 25
│       ├── 443
│       └── 80
│           └── robots.txt
├── scanme2.nmap.org -> 45.33.49.119
├── scanme.nmap.org -> 45.33.32.156
└── scanme.xml
```
You could now examine both robots.txt by hand or use:
```
$ nmap-query-xml scanme.xml --service http --pattern "file ./{ip}/{protocol}/{port}/robots.txt" | sh
./45.33.32.156/tcp/80/robots.txt: HTML document, ASCII text
./45.33.49.119/tcp/80/robots.txt: ASCII text
```
As you can see, the first file contains HTML. Probably a 404 or something. The second seems fine.

This concludes this rather simple introduction. I think, you got the point. Feel free to get creative!

## Tips & Tricks
### Multipe xml files
If you want to use several xml files in your directory, because of multiple scans, you can call `nmap-query-xml` with each and everyone using `xargs`:
```
$ ls *.xml
1.xml  2.xml  3.xml

$ ls *.xml | xargs -n1 nmap-query-xml
```
This is the equivalent of
```
$ nmap-query-xml 1.xml; nmap-query-xml 2.xml; nmap-query-xml 3.xml
```
### Multi-threading
If your scope contains a large amount of hosts and you want make your approach faster, then use GNU parallel instead of sh as a pipe: `nmap-query-xml your.xml --service http --pattern "yourtool {service}://{hostname}:{port}" | parallel --bar -j8` This will use 8 threads and show a progress bar.





