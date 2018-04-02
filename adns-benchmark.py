#!/usr/bin/env python
# -*- coding: utf-8 -*-

import adns
from time import time
import argparse
import sys
import numpy as np


"""
Proudly stolen (and adopted) from:
http://www.catonmat.net/blog/asynchronous-dns-resolution/

Install and compile adns and python bindings before running this!
"""

def get_line(filename):
     with open(filename) as file:
         for i in file:
             yield i.rstrip()



class AsyncResolver(object):
    def __init__(self, hosts, intensity=100):
        """
        hosts: a list of hosts to resolve
        intensity: how many hosts to resolve at once
        """
        self.hosts = hosts
        self.intensity = intensity
        self.adns = adns.init()

    def resolve(self):
        """ Resolves hosts and returns a dictionary of { 'host': 'ip' }. """
        resolved_hosts = {}
        active_queries = {}
        host_queue = self.hosts[:]

        def collect_results():
            for query in self.adns.completed():
                answer = query.check()
                host = active_queries[query]
                del active_queries[query]
                if answer[0] == 0:
                    ip = answer[3][0]
                    resolved_hosts[host] = ip
                elif answer[0] == 101: # CNAME
                    query = self.adns.submit(answer[1], adns.rr.A)
                    active_queries[query] = host
                else:
                    resolved_hosts[host] = None

        def finished_resolving():
            return len(resolved_hosts) == len(self.hosts)

        while not finished_resolving():
            while host_queue and len(active_queries) < self.intensity:
                host = host_queue.pop()
                query = self.adns.submit(host, adns.rr.A)
                active_queries[query] = host
            collect_results()

        return resolved_hosts






def main():

    parser = argparse.ArgumentParser( "DNS Perf Test" )
    parser.add_argument( 'domainfile', type=str)
    parser.add_argument( '--runs', type=str, default=30)
    args = parser.parse_args()
    domains = list(get_line(args.domainfile))
    
    timings = []
    for i in range(args.runs):
       print >> sys.stderr, i, 
       np.random.shuffle(domains)
       ar = AsyncResolver(domains, intensity=10000)
       start = time()
       resolved_hosts = ar.resolve()
       end = time()
       timings.append(end-start)
    print >>sys.stderr  
    print ("Took mean=%.2fs median=%.2fs stddev=%.2fs to resolve %d domains, (%d runs)") % (np.mean(timings), np.median(timings), np.std(timings), len(domains), args.runs)

if __name__ == '__main__':
    main()
