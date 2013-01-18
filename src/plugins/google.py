import json, urllib2, sys

#http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=hello%20world

def GrabData(query):
	opener = urllib2.build_opener()
	query = query.replace(' ', '%20')
	base = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={0}"
	url = base.format(query)
	data = opener.open(url).read()
	return data

def ParseJSON(data):
	jsonData = json.loads(data)
	temp = ""
	for item in jsonData["responseData"]["results"]:
		temp += (item["titleNoFormatting"] + '\n' + item["unescapedUrl"] + '\n')
	return temp

def Lookup(query):
	data = GrabData(query)
	result = ParseJSON(data)
	return result

if __name__ == "__main__":
	try: 
		print Lookup(sys.argv[1])
	except IndexError:
		query = str(raw_input('Enter a query: '))
		print Lookup(query)