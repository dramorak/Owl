import socket
import threading
import time

#A small http server that allows the implementer to construct their own response function. 
#Responsbility for the orrectness of the response function lies with the implementer.
class fla():
	#fixed length array
	def __init__(self, l):
		self.ir = [None] * l
		self.p  = 0
		self.length = l
		
	
	def push(self, el):
		t = self.ir[self.p]
		self.ir[self.p] = el
		self.p = (self.p + 1) % self.length

		return t

	def equals(self, seq):
		if len(seq) != self.length:
			return False

		for i in range(0, len(seq)):
			if self.ir[(self.p + i) % self.length] != seq[i]:
				return False
		return True


def read_stream(nxt, delim):
	# utility function to read a stream up to (but not including) a delimiting sequence.
	# 'nxt' function which, when called, returns the next object in the stream. 
	# delim is the delimiting byte sequence.
	last = fla(len(delim))
	out = bytearray(0)

	while not last.equals(delim):
		a = last.push(nxt())
		if a != None:
			out.append(a)
	return out

class HTMLServer():
	def __init__(self, PORT, callback_function):
		self.PORT = PORT
		self.cf = callback_function
		self.LOC = socket.gethostbyname(socket.gethostname())
		self.ADDR = (self.LOC, self.PORT)
		self.FORMAT = 'utf-8'
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind(self.ADDR)

	def start(self):
		def handle_client(conn, addr):
			#Read in html request, delimited by \r\n\r\n
			header = read_request(conn)

			#parse request into something readable
			header = parse(header)

			#hand the parsed request to user specified callback-function
			self.cf(conn, header)

			#close connection
			conn.close()

		def read_request(conn):
			def next_byte():
				return conn.recv(1)[0]
			return read_stream(next_byte, b'\r\n\r\n')

		def parse(header):
			header = header.decode(self.FORMAT)
			header = header.split('\n')

			out = {}

			#request line
			request = header[0].split(' ')
			out['request_type'] = request[0]
			out['URI'] = request[1]
			out['version'] = request[2]

			#auxilliary lines
			for x in range(1,len(header)):
				t = header[x].split(': ')
				out[t[0]] = t[1]

			return out
				
		#Listen for incomming connections
		#hand connection to 'handle connection' function
		print(f'[SERVER START] listening on {self.ADDR}')
		self.server.listen()
		while True:
			conn, addr = self.server.accept()
			thread = threading.Thread(target = handle_client, args=(conn,addr))
			thread.start()
			print(f'[NEW CONNECTION] {addr} connected. Active connections: {threading.activeCount() - 1}')

	def close(self):
		pass


if __name__ == '__main__':
	def respond(conn, header):
		html = """<!DOCTYPE html>
				  <html>
				  	<head>
					  <style>
					  	* { 
							background-color:rgb(200,200,200);
						  }
					  </style>
					</head>
					<body>
						<p>Congratulations, alex! You made a rudimentary html server</p>
					</body>
				  </html>
		"""
		html = html.encode('utf-8')
		
		response_header = f"""HTTP/1.1 200 OK
		Content-Length: {len(html)}
		Connection: Closed
		Content-Type: text/html
		Server: Owl/0.0.1 (Win32)

		"""
		response_header = response_header.encode('utf-8')

		if header['request_type'] == 'GET':
			conn.send(response_header + html)

	def print_request(conn, header):
		print(header)

	server = HTMLServer(8000, respond)
	server.start()

