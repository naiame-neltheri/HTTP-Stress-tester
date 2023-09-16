import jwt, argparse, json, os

def sign(key, payload):
	constructedPayload = {}
	for item in payload.split(","):
		key,value = item.split("=")
		constructedPayload[key] = value
	try:
		encoded = jwt.encode(constructedPayload, "" if key == 0 else key, algorithm="HS256")
		return encoded
	except Exception as err:
		print(err)
		return False

def decode(key, token):
	try:
		decoded = jwt.decode(token, key, algorithms=["HS256"])
		return True
	except jwt.exceptions.InvalidSignatureError:
		return False
	except Exception as err:
		print(err)
		return False

def findKey(wordlist, token):
	if os.path.exists(wordlist):
		print(f"Searching key from wordlist: {args.getKey[0]}...")
		with open(wordlist, 'r') as f:
			_line = f.readline()
			while _line:
				print(f"Trying key : {_line}")
				if decode(_line, token):
					print(f"Key found {_line}")
					break
				try:
					_line = f.readline()
				except UnicodeDecodeError:
					continue
		print("No key found in given list")
	else:
		if decode(wordlist, token):
			print(f"Supplied key {wordlist} is correct")
		else:
			print(f"Supplied key {wordlist} is incorrect")

if "__main__" in __name__:
	parser = argparse.ArgumentParser(description = "Python JWT tool")
	parser.add_argument('--sign', help = "Sign JWT with specified key and payload, 0 for blank sign. Ex: jwt.py --sign 0 key1=value1,key2=value2", nargs=2)
	parser.add_argument('--getKey', help = "Generate key from given wordlist. Ex jwt.py --getKey wordlist.txt|key-to-test JWTTOKEN", nargs=2)

	args = parser.parse_args()
	if args.sign:
		print(sign(args.sign[0], args.sign[1]))
	elif args.getKey:
		findKey(args.getKey[0], args.getKey[1])