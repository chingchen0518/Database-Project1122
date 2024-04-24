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
    tiga_bahasa=[{"bahasa":"Malay","salam":"selamat pagi"},
                 {"bahasa":"English","salam":"Good morning"},
                {"bahasa":"Cina","salam":"早安"},
                {"bahasa": "French", "salam": "Bonjour"}
    ]
    myname="Ching Chen"
    yes_or_no = 2;
    statements = ["Yes,it is successful","It is still ongoing","It is fail"]

    return render(request,
                  "index.html",
                  {"salamat":tiga_bahasa,"name":myname,"yes_or_no":yes_or_no,"statements":statements})

def aboutme(request):
    return render(request,"aboutme.html")

def map(request):
    return render(request,"map.html")

def register(request):
    return render(request,"Register.html")

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