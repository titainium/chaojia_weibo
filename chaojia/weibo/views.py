from django.shortcuts import render_to_response
from django.http import HttpResponse
from weibo.models import rdb

def weibo_home(request):
    #return render_to_response('weibo_home.html')
    return HttpResponse(rdb.info())