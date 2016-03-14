from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import find_similar
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def index(request):
    output_list = ''
    output=''
    if request.GET.get('search'):
        search = request.GET.get('search')
        output_list = find_similar(search)
        paginator = Paginator(output_list, 10) # Shows only 10 records per page
        page = request.GET.get('page')
        try:
            output = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            output = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 7777), deliver last page of results.
            output = paginator.page(paginator.num_pages)
    return render_to_response('project_template/index.html', 
                          {'output': output,
                           'magic_url': request.get_full_path(),
                           })

    #=======================================================================================
    #OLD IMPLEMENTATION
    # if request.method == 'POST':
    #  	form = QueryForm(request.POST)
    #  	if form.is_valid():
    #  		q = form.cleaned_data['q']
    #  		output = find_similar(q)
    #  		return render(request, 'project_template/index.html', {'output': output[:10]})
    #  		#return HttpResponse('Similar Messages (top 10): \n'+output)
    # else:
    #     form = QueryForm()
    #     return render(request, 'project_template/index.html', {'form': form})
    #=======================================================================================