import json
from collections import defaultdict
text_file = open("Beeradvocate.txt", "r").read().split("\n\n")
final_dict = defaultdict(list)
for idx,elem in enumerate(text_file):
	if len(final_dict.keys()) > 1000:
		break
	print("%d/%d" % (idx,len(text_file)))
	elem = text_file[idx]
	values = elem.split("\n")
	inner_dict = {}
	for indx in values[1:]:
		colon_loc = indx.find(":")
		key,value = indx[0:colon_loc], indx[colon_loc+2:]
		if key == 'review/profileName':
			continue
		inner_dict[key.replace("beer/", "").replace("review/","")] = value.replace("\t", " ")
	print(values[0])
	final_dict[values[0].split("/name: ")[1]].append(inner_dict)

json.dump(final_dict, open('beer_1000.json', 'w'), indent=4, sort_keys=True)