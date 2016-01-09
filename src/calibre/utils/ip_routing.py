#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import subprocess, re
from calibre.constants import iswindows, isosx

def get_address_of_default_gateway(family='AF_INET'):
    import netifaces
    ip = netifaces.gateways()['default'][getattr(netifaces, family)][0]
    if isinstance(ip, bytes):
        ip = ip.decode('ascii')
    return ip

def get_addresses_for_interface(name, family='AF_INET'):
    import netifaces
    for entry in netifaces.ifaddresses(name)[getattr(netifaces, family)]:
        if entry.get('broadcast'):  # Not a point-to-point address
            addr = entry.get('addr')
            if addr:
                if isinstance(addr, bytes):
                    addr = addr.decode('ascii')
                yield addr

if iswindows:

    def get_default_route_src_address():
        # Use -6 for IPv6 addresses
        raw = subprocess.check_output('route -4 print 0.0.0.0'.split()).decode('utf-8', 'replace')
        in_table = False
        default_gateway = get_address_of_default_gateway()
        for line in raw.splitlines():
            parts = line.strip().split()
            if in_table:
                if len(parts) == 6:
                    network, destination, netmask, gateway, interface, metric = parts
                elif len(parts) == 5:
                    destination, netmask, gateway, interface, metric = parts
                if gateway == default_gateway:
                    return interface
            else:
                if parts == 'Network Destination Netmask Gateway Interface Metric'.split():
                    in_table = True


elif isosx:

    def get_default_route_src_address():
        # Use -inet6 for IPv6
        raw = subprocess.check_output('route -n get -inet default'.split()).decode('utf-8')
        m = re.search(r'^\s*interface:\s*(\S+)\s*$', raw, flags=re.MULTILINE)
        if m is not None:
            interface = m.group(1)
            for addr in get_addresses_for_interface(interface):
                return addr
else:

    def get_default_route_src_address(to='1.1.1.1'):
        # Use -6 for IPv6 addresses
        raw = subprocess.check_output(('ip -4 route get ' + to).split()).decode('utf-8')
        m = re.search('^%s\s+via\s+%s\s+.+?src\s+(.+)' % (to, get_address_of_default_gateway()), raw, flags=re.MULTILINE)
        if m is not None:
            return m.group(1)

if __name__ == '__main__':
    print(get_default_route_src_address())