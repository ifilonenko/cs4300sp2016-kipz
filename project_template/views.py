from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar
from .test import find_similar_features
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def index(request):
	beer_output_list = ''
	features_output_list = ''
	output_list = ''
	output = ''
	if request.GET.get('search') and request.GET.get('search_features'):
		beer_search = request.GET.get('search')
		features_search = request.GET.get('search_features')
		beer_output_list = find_similar(beer_search)
		#features_output_list = find_similar_features(features_search)
		#paginator_feat = Paginator(features_output_list, 10)
		paginator_beer = Paginator(beer_output_list, 10)
		page = request.GET.get('page')
		try:
			output = paginator_beer.page(page)
		except PageNotAnInteger:
			output = paginator_beer.page(1)
		except EmptyPage:
			output = paginator_beer.page(paginator_beer.num_pages)
	elif request.GET.get('search'):
		search = request.GET.get('search')
		output_list = find_similar(search)
		paginator = Paginator(output_list, 10)
		page = request.GET.get('page')
		try:
			output = paginator.page(page)
		except PageNotAnInteger:
			output = paginator.page(1)
		except EmptyPage:
			output = paginator.page(paginator.num_pages)
	elif request.GET.get('search_features'):
		features_search = request.GET.get('search_features')
		features_output_list = find_similar_features(features_search)
		paginator = Paginator(features_output_list, 10)
		page = request.GET.get('page')
		try:
			output = paginator.page(page)
		except PageNotAnInteger:
			output = paginator.page(1)
		except EmptyPage:
			output = paginator.page(paginator.num_pages)
	return render_to_response('project_template/index.html', 
						  {'output': output,
						   'magic_url': request.get_full_path(),
						   })
