from django.shortcuts import render_to_response

def weibo_home(request):
    return render_to_response('weibo_home.html')