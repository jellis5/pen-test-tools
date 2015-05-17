#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, sys
import multiprocessing as mp
from http.client import HTTPConnection
from queue import Queue

PROCESSES = 20

def sendReq(qIn):
	while not qIn.empty():
		try:
			conn = HTTPConnection(hostname)
			line = qIn.get()
			conn.request("HEAD", "/" + line, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0'})
			readResp(conn.getresponse(), line)
		# silently reconnect upon timeout
		except socket.gaierror:
			pass

def readResp(resp, line):
	if resp.status != 404:
		print(resp.status, "-", "/" + line)
	
if len(sys.argv) != 3:
	sys.exit("Invalid arguments!\nUsage: python3 {} <hostname[:http-port]> <dirfile>".format(sys.argv[0]))
hostname = sys.argv[1] + ":80"
if ":" in sys.argv[1]:
	hostname = sys.argv[1]
print()

if __name__ == '__main__':
	try:
		with open(sys.argv[2]) as f:
			qIn = mp.Queue()
			for line in f:
				qIn.put(line.strip())
			processes = [mp.Process(target=sendReq, args=(qIn,)) for x in range(PROCESSES)]
			for p in processes:
				p.start()
			for p in processes:
				p.join()
	except IOError:
		sys.exit("Directories file not found!")
