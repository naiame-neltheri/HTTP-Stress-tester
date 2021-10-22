#!/bin/python3

import urllib3, time
import requests, sys
import argparse, threading

consumedLst = []

# this function visits given url, if error happens it will return a message.
def initiate_full_con(url, timeout, raw_header, id, ssl_verify):
	start = time.time()
	header = {raw_header.split(":")[0] : raw_header.split(":")[1].strip()}
	try:
		if ssl_verify:
			r = requests.get(url, headers = header, timeout = timeout)                 # GET request triggers here with ssl verification
		else:
			urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  
			r = requests.get(url, verify = False, headers = header, timeout = timeout) # GET request triggers here without check ssl
		consumedLst.append(float(time.time() - start))
		if r.status_code != 200:
			# print(f"[-] Invalid HTTP status code received : {r.status_code}")
			return f"[-] Invalid HTTP status code received : {r.status_code}"
		# print(f"[+] Thread {id} : Consumed time for HTTP request {float(time.time() - start):.2f} second")
		return True
	except requests.exceptions.MissingSchema:
		print("[-] Error schema is not supplied, please provide http or https schema to URL")
		return False
	except requests.exceptions.ReadTimeout:
		print(f"[*] Timeout occured on {url} with timeout set to : {timeout} sec")
		return False
	except requests.exceptions.SSLError as err:
		print(f"[!] SSL error occured use -k option to skip it")
		print(err)
		return False

if "__main__" in __name__:
	parser = argparse.ArgumentParser(description = "HTTP Load tester by Naiame Nel'theri")
	parser.add_argument("max", help = "Number of requests to send", type = int)
	parser.add_argument("url", help = "URL for web service", type = str)
	parser.add_argument("-t", dest = "thread", default = [1], nargs = 1, help = "Thread count, default is 1", type = int)
	parser.add_argument("-H", dest = "header", default = None, nargs = 1, help = "Custom header, ex: Authorization: Bearer test", type = str)
	parser.add_argument("-T", dest = "timeout", default = [30], nargs = 1, help = "Set timeout for warning message", type = float)
	parser.add_argument("-k", dest = "ssl_verify", default = True, action = "store_false", help = "Set SSL verification to false")

	args = parser.parse_args()
	print(args)

	header = None
	if args.header:
		header = args.header[0]

	threads = []
	cnt = 0 # counter
	while cnt < args.max:
		for i in range(0, args.thread[0]):
			if cnt > args.max:
				break
			t = threading.Thread(target = initiate_full_con, args=(args.url, args.timeout[0], header, i, args.ssl_verify,))
			t.start()
			threads.append(t)
			cnt += 1
			print(f"\r[+] Total of {cnt} requests sent", end="", flush = True)

	for thread in threads:
		thread.join()
	avgConsumedTime = sum(consumedLst) / len(consumedLst)
	print(f"\n[+] Average Time : {avgConsumedTime:.2f} second"))
