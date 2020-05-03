#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This software must not be used by military or secret service organisations.
# License: TODO
# TODO: PEP 8

import sys, argparse
from libnmap.parser import NmapParser

greeter = '''
 ▐ ▄ • ▌ ▄ ·.  ▄▄▄·  ▄▄▄·    .▄▄▄  ▄• ▄▌▄▄▄ .▄▄▄   ▄· ▄▌    ▐▄• ▄ • ▌ ▄ ·. ▄▄▌  
•█▌▐█·██ ▐███▪▐█ ▀█ ▐█ ▄█    ▐▀•▀█ █▪██▌▀▄.▀·▀▄ █·▐█▪██▌     █▌█▌▪·██ ▐███▪██•  
▐█▐▐▌▐█ ▌▐▌▐█·▄█▀▀█  ██▀·    █▌·.█▌█▌▐█▌▐▀▀▪▄▐▀▀▄ ▐█▌▐█▪     ·██· ▐█ ▌▐▌▐█·██▪  
██▐█▌██ ██▌▐█▌▐█ ▪▐▌▐█▪·•    ▐█▪▄█·▐█▄█▌▐█▄▄▌▐█•█▌ ▐█▀·.    ▪▐█·█▌██ ██▌▐█▌▐█▌▐▌
▀▀ █▪▀▀  █▪▀▀▀ ▀  ▀ .▀       ·▀▀█.  ▀▀▀  ▀▀▀ .▀  ▀  ▀ •     •▀▀ ▀▀▀▀  █▪▀▀▀.▀▀▀ '''
for c in "█▐▌▄▀":
    greeter = greeter.replace(c, "\u001b[32m" + c + "\u001b[0m")
version = "0.0.3#beta"
url = "https://github.com/honze-net/nmap-query-xml"

parser = argparse.ArgumentParser(description="", epilog="Full documentation: %s\nThis software must not be used by military or secret service organisations." % url, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("xml", help="path to Nmap XML file")
parser.add_argument("--service", help="Nmap service name to filter for. Default: Empty", default="", dest="service")
parser.add_argument("--pattern", help="Pattern for output. Default: %(default)s", default="{service}{s}://{hostname}:{port}", dest="pattern")
parser.add_argument("--state", help="Select a port state. Use \"all\" for all. Default: %(default)s", default="open", dest="state")

if len(sys.argv) == 1: # If no arguments are specified, print greeter, help and exit.
    print(greeter)
    print(("version %s %s\n" % (version, url)).center(80))
    parser.print_help()
    sys.exit(0) 
args = parser.parse_args()

try:
    report = NmapParser.parse_fromfile(args.xml)
except IOError:
    print("Error: File %s not found." % args.xml)
    sys.exit(1)

for host in report.hosts:
    for service in host.services:
        if (service.state == args.state or args.state == "all") and (args.service == "" or service.service in args.service.split(",")): # TODO: Test if this is precise enough
            line = args.pattern
            line = line.replace("{xmlfile}", args.xml)
            line = line.replace("{hostname}", host.address if not host.hostnames else host.hostnames[0]) # TODO: Fix naive code.
            line = line.replace("{hostnames}", host.address if not host.hostnames else ", ".join(list(set(host.hostnames)))) # TODO: Fix naive code.
            line = line.replace("{ip}", host.address)
            line = line.replace("{service}", service.service)
            line = line.replace("{s}", "s" if service.tunnel == "ssl" else "")
            line = line.replace("{protocol}", service.protocol)
            line = line.replace("{port}", str(service.port))
            line = line.replace("{state}", str(service.state))
            print("%s" % line)
