#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, re, sys
import multiprocessing as mp
from http.client import HTTPConnection
from queue import Queue

PROCESSES = 3
SPEED = 3
CUSTOM404 = ""
OUTPUTFILE = False

def testHost(hostname):
	"""Test if host appears to be alive.
	
	Args:
		hostname: hostname of target
	Returns:
		True if host appears to be alive, False otherwise
	"""
	print("Testing to see if host is alive...")
	conn = HTTPConnection(hostname)
	conn.request("GET", "/", headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0'})
	if conn.getresponse():
		return True
	return False

def sendReq(qIn):
	"""Send next in queue as request to hostname. Uses GET or HEAD.
	
	Args:
		qIn: queue that contains lines of directory file
	"""
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
	"""Read response from sendReq to determine if resource exists.
	
	Args:
		resp: HTTPResponse object
		line: resource name currently requested
	"""
	outputLine = str(resp.status) + " - " + line
	if not OUTPUTFILE:
		if not CUSTOM404:
			if resp.status != 404:
				print(outputLine)
		else:
			body = resp.read().decode('utf-8')
			if CUSTOM404 not in body:
				print(outputLine)
	else:
		global fOut
		if not CUSTOM404:
			if resp.status != 404:
				fOut.write(outputLine + "\n")
				fOut.flush()
		else:
			body = resp.read().decode('utf-8')
			if CUSTOM404 not in body:
				fOut.write(outputLine + "\n")
				fOut.flush()
				
optionsText = """Options MUST come after the required arguments:
--speed=[1 (slowest) - 5 (fastest)]; default 3
-404 looks in cwd for 404.txt and uses that as custom 404 signature; default is HTTP status 404 code
-o writes output to file in cwd with name \"[hostname]_[directory file]\"; default stdout"""
	
try:
	if len(sys.argv) == 1:
		raise ValueError
	elif len(sys.argv) == 2:
		if sys.argv[1] == "-h":
			sys.exit(optionsText)
		else:
			raise ValueError
	elif len(sys.argv) >= 3:
		hostname = sys.argv[1] + ":80"
		if ":" in sys.argv[1]:
			hostname = sys.argv[1]
		if len(sys.argv) > 3:
			reSpeed = re.compile(r'--speed=[1-5]')
			re404 = re.compile(r'-404')
			reOutput = re.compile(r'-o')
			for option in sys.argv[3:]:
				if reSpeed.match(option):
					SPEED = int(option[8]) # index 8 is number in option
				elif re404.match(option):
					try:
						with open('404.txt') as f:
							CUSTOM404 = f.read().strip()
					except IOError:
						sys.exit("Custom 404.txt file not found!")
				elif reOutput.match(option):
					OUTPUTFILE = True
					try:
						fOut = open(sys.argv[1]+"_"+sys.argv[2], 'w')
					except IOError:
						sys.exit("Could not open output file!")		
		PROCESSES *= SPEED
	print()
except ValueError:
	sys.exit("Invalid arguments!\nUsage: python3 {} <hostname[:http-port]> <dirfile>\n\"python3 {} -h\" for help and options.".format(sys.argv[0], sys.argv[0]))

if __name__ == '__main__':
	try:
		if not testHost(hostname):
			sys.exit("Host does not seem responsive...")
		else:
			print("Host alive!")
		print("Scanning...")
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
	finally:
		if OUTPUTFILE:
			fOut.close()
