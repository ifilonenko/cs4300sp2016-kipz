from django.shortcuts import render
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar

# Create your views here.
def index(request):
    if request.method == 'POST':#
     	form = QueryForm(request.POST)
     	if form.is_valid():
     		q = form.cleaned_data['q']
     		output = find_similar(q)
     		return render(request, 'project_template/result.html', {'output': output[:10]})
     		#return HttpResponse('Similar Messages (top 10): \n'+output)
    else:#
        form = QueryForm()
    	return render(request, 'project_template/index.html', {'form': form})