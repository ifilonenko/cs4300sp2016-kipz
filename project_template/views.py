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
	output = []
	if request.GET.get('search'):
		search = request.GET.get('search')
	else:
		search = ""
	if request.GET.get('version'):
		version = request.GET.get('version')
	else:
		version = "new"
	request_type = (request.META["HTTP_ACCEPT"].split(",")[0])
	if (request_type == "application/json"):
		output = find_similar(search, 10)
		return JsonResponse(output, content_type="application/json", safe=False)
		
	elif (request_type == "text/html"):
		return render_to_response('project_template/index.html', 
							  {
							   'search_params': search
							  })

