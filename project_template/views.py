from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json


# Create your views here.
def index(request):
	beer_output_list = ''
	features_output_list = ''
	output_list = ''
	output = ''
	if request.GET.get('search'):
		search = request.GET.get('search')
		output_list = find_similar(search, 25)
		page = request.GET.get('page')
		if (page != None and page != ""):
			output = output_list[0+int(page)*5:5+int(page)*5]
		else:
			page = 0
			output = output_list[0:5]

	print request.META["CONTENT_TYPE"]
	print output
	if (request.META["CONTENT_TYPE"] == "text/plain"):
		return render_to_response('project_template/index.html', 
							  {'output': output,
							   'magic_url': request.get_full_path(),
							   'search_params': search,
							   'page_params': page
							   })
	elif (request.META["CONTENT_TYPE"] == "application/json"):
		data = json.dumps(output)
		return HttpResponse(data, content_type="application/json")

