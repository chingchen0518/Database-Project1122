from django.shortcuts import HttpResponse,render,redirect
import json
from django.http import JsonResponse
from django.db import connection

#引入 Table
from my_app.models import Member
#引入 Table結束

def index(request):
    variables=request.GET['id']
    context = {'name': 'John'}
    return HttpResponse(context['name']+" is id="+variables)

def getdata(request):
    list={20030518,20040124}
    list2={"name":"Chi1111111111111111111ng Chen","Age":"21","school":'NSYSU'}
    variables=json.dumps(list2)
    # return JsonResponse(list,safe=False)
    return HttpResponse(variables)
    # return HttpResponse("I am "+list2["name"]+" from "+list2["school"]+", and I am "+list2["Age"]+" years old.")

def homepage(request):
    return render(request,"homepage.html")

def aboutme(request):
    return render(request,"aboutme.html")

def map(request):
    return render(request,"map.html")

def register(request):
    return render(request,"register2.html")

def register_received(request):
    # name=request.POST['name']
    # pwd=request.POST['password']
    # cursor.execute("insert into testing(name,password) values(%s,%s)",(name,pwd))
    return HttpResponse("")

def login_page(request):
    return render(request,"login.html")

def login_act(request):
    username = request.POST['username']
    pwd = request.POST['password']

    members = Member.objects.filter(username=username)

    return redirect('/login/')