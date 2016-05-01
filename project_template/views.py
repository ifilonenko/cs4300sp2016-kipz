from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse


# Create your views here.
def index(request):
	beer_output_list = ''
	features_output_list = ''
	output_list = []
	output = []
	if request.GET.get('search'):
		search = request.GET.get('search')
		page = request.GET.get('page')
		if ((page == None) or (page == "")):
			page = 0
	else:
		search = ""
		page = 0

	request_type = (request.META["HTTP_ACCEPT"].split(",")[0])
	if (request_type == "application/json"):
		output_list = find_similar(search, 5)
		if (page != 0):
			output = output_list[0+int(page)*5:5+int(page)*5]
		else:
			page = 0
			output = output_list[0:5]
		return JsonResponse(output, content_type="application/json", safe=False)
		
	elif (request_type == "text/html"):
		return render_to_response('project_template/index.html', 
							  {
							   'search_params': search,
							   'page_params': page
							   })

