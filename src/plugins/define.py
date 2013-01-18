import json, urllib2, sys

def GrabData(query):
	opener = urllib2.build_opener()
	base = "http://www.google.com/dictionary/json?callback=a&sl=en&tl=en&q={0}"
	url = base.format(query)
	data = opener.open(url).read()[2:-10]
	data = data.replace('\\x27', "'")
	data = data.replace('\\','')	#google's json contains invalid escape characters, nasty fix
	return data

def ParseJSON(data):
	jsonData = json.loads(data)
	try:
		result = jsonData["primaries"][0]["entries"][1]["terms"][0]["text"]
	except IndexError:
		result = jsonData["primaries"][0]["entries"][0]["terms"][0]["text"]
	except KeyError:
		result = 'Invalid query: {0}'.format(jsonData["query"])
	return result

def Definition(query):
	data = GrabData(query)
	definition = ParseJSON(data)
	return definition

if __name__ == "__main__":
	try: 
		print Definition(sys.argv[1])
	except IndexError:
		query = str(raw_input('Enter a query: '))
		print Definition(query)