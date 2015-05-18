#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, re, sys
import multiprocessing as mp
from http.client import HTTPConnection
from queue import Queue

PROCESSES = 5
SPEED = 3
CUSTOM404 = ""

def sendReq(qIn):
	while not qIn.empty():
		try:
			conn = HTTPConnection(hostname)
			line = qIn.get()
			conn.request("HEAD" if not CUSTOM404 else "GET", "/" + line, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0'})
			readResp(conn.getresponse(), line)
		# silently reconnect upon timeout
		except socket.gaierror:
			pass

def readResp(resp, line):
	outputLine = str(resp.status) + " - " + line
	if not CUSTOM404:
		if resp.status != 404:
			print(outputLine)
	else:
		body = resp.read().decode('utf-8')
		if CUSTOM404 not in body:
			print(outputLine)
	
try:
	if len(sys.argv) == 1:
		raise ValueError
	if len(sys.argv) == 2:
		if sys.argv[1] == "-h":
			sys.exit("Options MUST come after the required arguments:\n--speed=[1 (slowest) - 5 (fastest)]; default 3\n-404 looks in cwd for 404.txt and uses that as custom 404 signature; default is HTTP status 404 code\n")
		else:
			raise ValueError
	if len(sys.argv) >= 3:
		if len(sys.argv) > 3:
			reSpeed = re.compile(r'--speed=[1-5]')
			re404 = re.compile(r'-404')
			for option in sys.argv[3:]:
				if reSpeed.match(option):
					SPEED = int(option[8]) # index 8 is number in option
				elif re404.match(option):
					try:
						with open('404.txt') as f:
							CUSTOM404 = f.read().strip()
					except IOError:
						sys.exit("Custom 404.txt file not found!")
		PROCESSES *= SPEED
		hostname = sys.argv[1] + ":80"
		if ":" in sys.argv[1]:
			hostname = sys.argv[1]
		
	print()
except ValueError:
	sys.exit("Invalid arguments!\nUsage: python3 {} <hostname[:http-port]> <dirfile>\n\"python3 {} -h\" for help and options.".format(sys.argv[0], sys.argv[0]))

if __name__ == '__main__':
	try:
		with open(sys.argv[2]) as f:
			qIn = mp.Queue()
			for line in f:
				qIn.put(line.strip())
			processes = [mp.Process(target=sendReq, args=(qIn,)) for x in range(PROCESSES)]
			for p in processes:
				p.daemon = True
				p.start()
			for p in processes:
				p.join()
	except IOError:
		sys.exit("Directories file not found!")
	except KeyboardInterrupt:
		sys.exit("Keyboard Interrupt. Exiting...")
