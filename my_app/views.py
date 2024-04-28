from django.shortcuts import HttpResponse,render,redirect
import json
from django.http import JsonResponse
from django.db import connection
from django.db.models import Min
from django.urls import reverse_lazy
from django.views.generic import DeleteView

#引入 Table
from my_app.models import Member, House, Image,Equipment
#引入 Table結束

class HouseDeleteView(DeleteView):
    model = House
    success_url = reverse_lazy("house_lists")
    template_name = 'delete.html'
    pk_url_kwarg = 'hId' #告訴他用url中的哪個東西作爲primarykey

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

def house_list(request):
    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId LIKE %s AND House.hId=Info.hId_id',['KH%'])
    return render(request, "house_list.html",{'rows': rows})

def house_rent_cont(request,hId):
    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId=%s AND House.hId=Info.hId_id', [hId])
    image = Image.objects.raw('SELECT path FROM Image WHERE Image.hId_id=%s', [hId])
    equipment = Equipment.objects.raw('SELECT * FROM Equipment WHERE Equipment.hId_id=%s', [hId])

    return render(request, "house_rent_cont.html",{'row': rows[0],'images':image,'equipment':equipment[0]})

def upload_page(request):
    # age = request.POST['age']
    # print(age)


    return render(request, "add_house/add_house.html")

def add_house(request):
    region = request.POST['region']
    # address = request.POST['address']
    # age = request.POST['age']
    # room = request.POST['room']
    # bath = request.POST['bath']
    # living = request.POST['living']
    # size = request.POST['size']
    # type = request.POST['type']
    # level = request.POST['level']
    # price = request.POST['price']

    #Count next id
    # latest_id = House.objects.filter(region=region).latest('hId')
    # prefix = latest_id.hId[:-2]  # 取得 ID 前綴，即 'KH'
    # number_part = int(latest_id.hId[-2:])  # 取得數字部分，轉換為整數，即 20
    # next_number = number_part + 1  # 數字部分加 1，即 21
    # next_id = f"{prefix}{next_number:02}"  # 將 ID 前綴與新的數字部分結合，並確保數字部分有兩位數，即 'KH21'

    # print(price)
    # with connection.cursor() as cursor:
    #     cursor.execute('INSERT INTO House VALUES (%s, %s, %s, %s)',(next_id, 0,"tesitng",region))

    # print()

    # print(room)
    # print(bath)
    # print(living)
    # print(size)
    # print(type)
    # print(level)

    return render(request, "add_house/add_house.html")


