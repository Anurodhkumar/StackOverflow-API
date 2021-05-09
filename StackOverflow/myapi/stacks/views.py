from django.shortcuts import render
import json
import requests
from django.http import HttpResponse,JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import datetime,timedelta

@cache_page(60*60*2)
def home(request):
    #import pdb;pdb.set_trace()
    query = request.GET.get('query', None)
    try:
        page = request.GET.get('page', 1)
    except:
        page = 1
    id = request.session.session_key
    value = request.session.get(id, 'empty')
    min_value = request.session.get(id+'min', 'empty')
    if value !=None and value!='empty' and min_value !='empty':
        last_time = datetime.strptime(value[0],'%Y-%m-%d %H:%M:%S.%f')
        last_min = datetime.strptime(min_value[0],'%Y-%m-%d %H:%M:%S.%f')
        diff = datetime.now() -  last_time 
        diff_min = datetime.now() -  last_min
        if diff != '':
            if value[1] <100:
                request.session[id] = [str(last_time),value[1]+1]
            else:
                return HttpResponse('100 calls in a 1 day is done')

        if diff_min != '':
            if min_value[1] >=5:
                request.session[id+'min'] = [str(datetime.now()),1]
                return HttpResponse('5 calls in a 1 minutes is done')
            elif diff_min < timedelta(minutes=1):
                request.session[id+'min'] = [str(last_min),min_value[1]+1]
            elif diff_min > timedelta(minutes=1):
                request.session[id+'min'] = [str(datetime.now()),1]
    else:
        request.session[id] = [str(datetime.now()),1]
        request.session[id+'min'] = [str(datetime.now()),1]
    url = 'https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&site=stackoverflow&' + query
    response = requests.get(url, headers={'Authorization': 'access_token 5c5RR62TnSG7VCZ62ysfPQ(('})
    value = response.json()['items']
    paginator = Paginator(value, 10)
    pagecount = int(page) *10 
    try:
        users = paginator.page(page)
        params = {'users' : users,'query':query,'page':pagecount}
        return render(request, 'result.html', params)
    except:
        return HttpResponse('No Answers found.Please check Query')
    