beer_to_brewery = {}
brewery_to_beer = defaultdict(list)
counter = 0
for key in transcripts.keys():
	print("%d,%d" % (counter, len(transcripts.keys())))
	beer_name = key.encode('ascii', 'ignore')
	brewer_id = (transcripts[key]['brewerId'])
	brewery = str(brewer_id)
	url = 'http://www.beeradvocate.com/beer/profile/' + brewery + '/'
	counter+=1
	req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
	try:
		con = urllib2.urlopen( req )
	except:
		print("this is odd")
		continue
	val = con.read()
	brewer_name = val[val.find('<title>') + 7:val.find(' | ')]
	brewer_name
	beer_to_brewery[beer_name] = brewer_name
	brewery_to_beer[brewer_name].append(beer_name)
	print(beer_name)
	print(brewer_name)

new_brewery_to_beer = {}
new_beer_to_brewery = {}
for key in brewery_to_beer.keys():
	print(key)
	values = brewery_to_beer[key]
	brewery_name = key.decode('utf-8').encode('ascii', 'ignore')
	new_brewery_to_beer[brewery_name] = values
	for beer in values:
		new_beer_to_brewery[beer] = brewery_name
