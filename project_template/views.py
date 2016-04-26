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
		output_list = find_similar(search, 2)
		# paginator = Paginator(output_list, 10)
		# page = request.GET.get('page')
		# try:
		# 	output = paginator.page(page)
		# except PageNotAnInteger:
		# 	output = paginator.page(1)
		# except EmptyPage:
		# 	output = paginator.page(paginator.num_pages)
	print request.META["CONTENT_TYPE"]
	if (request.META["CONTENT_TYPE"] == "text/plain"):
		return render_to_response('project_template/index.html', 
							  {'output': output_list,
							   'magic_url': request.get_full_path(),
							   'search_params': search
							   })
	elif (request.META["CONTENT_TYPE"] == "application/json"):
		print("hello")
		data = json.dumps(output_list)
		return HttpResponse(data, content_type="application/json")

