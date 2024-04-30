from django.shortcuts import HttpResponse,render,redirect
import json
from django.http import JsonResponse
from django.db import connection
from django.db.models import Min
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.core.exceptions import ObjectDoesNotExist
import datetime


#引入 Table
from my_app.models import Member, House, Image,Equipment,User,Member
#引入 Table結束

class HouseDeleteView(DeleteView):
    model = House
    success_url = reverse_lazy("house_lists")
    template_name = 'delete.html' #之後加一個取消
    pk_url_kwarg = 'hId' #告訴他用url中的哪個東西作爲primary_key

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
    if 'user' in request.session:
        return render(request, "homepage.html",{'user':request.session['user']})
    return render(request,"homepage.html",{'user':0})

def aboutme(request):
    return render(request,"aboutme.html")

def map(request):
    return render(request,"map.html")

def register(request):
    if 'user' in request.session:
        return redirect('homepage')

    else:
        return render(request,"register2.html")

def register_received(request):
    fields=['username','realname','phone','password','email','gender']
    Users = {field: request.POST[field] for field in fields}

    # Count next mId
    try:
        latestid = Member.objects.latest('mId')
        mId = int(latestid.mId)+1
    except ObjectDoesNotExist:
        mId ="888"

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO User  VALUES (%s, %s)',(Users['username'],Users['password']))
        cursor.execute('INSERT INTO Member VALUES (%s, %s, %s, %s, %s, %s, %s)',(mId,Users['gender'],Users['email'],Users['phone'],None,Users['realname'],Users['username']))

    request.session['user'] = Users['username']
    return redirect('homepage')

def login_page(request):
    if 'user' in request.session:
        return redirect('homepage')

    else:
        return render(request,"login.html")


def login_act(request):
    username = request.POST['username']
    pwd = request.POST['password']

    user = User.objects.filter(username=username)
    if user:
        if user[0].password==pwd:
            request.session['user'] = username
            print(request.session['user'])
            return redirect("homepage")
        else:
            return HttpResponse("Wrong username or password")
            return redirect('/login/')

def logout(request):
    del request.session['user']
    return redirect("homepage")
def house_list(request):
    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId LIKE %s AND House.hId=Info.hId_id',['KH%'])

    return render(request, "house_list.html",{'rows': rows})

def house_rent_cont(request,hId):
    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId=%s AND House.hId=Info.hId_id', [hId])
    image = Image.objects.raw('SELECT path FROM Image WHERE Image.hId_id=%s', [hId])
    equipment = Equipment.objects.raw('SELECT * FROM Equipment WHERE Equipment.hId_id=%s', [hId])

    return render(request, "house_rent_cont.html",{'row': rows[0],'images':image,'equipment':equipment[0]})

def upload_page(request):
    if 'user' in request.session:
        return render(request, "add_house/add_house_v2.html")

    else:
        return redirect('/login/')

def add_house(request):
    current_date = datetime.date.today()
    # House
    region = request.POST['region']
    title = request.POST['title']
    # Info
    fields = ['address', 'room', 'bath', 'living', 'size', 'type', 'level', 'price']
    Info = {field: request.POST[field] for field in fields}
    print(Info)

    # Rdetails
    fields = ['parking','pet','cook','direction','level','security','management','period','bus','train','mrt','age']
    Rdetails = {field: request.POST.get(field, '0') for field in fields}
    print(Rdetails)

    # Equipments
    fields = ['sofa', 'tv', 'washer', 'wifi', 'bed', 'refrigerator', 'heater', 'channel4', 'cabinet', 'aircond', 'gas']
    Equip = {field: request.POST.get(field, '0') for field in fields}

    # Count next id
    if(House.objects.filter(region=region)):
        latest_id = House.objects.filter(region=region).latest('hId')
        prefix = latest_id.hId[:-2]  # 取得 ID 前綴，即 'KH'
        number_part = int(latest_id.hId[-2:])  # 取得數字部分，轉換為整數，即 20
        next_number = number_part + 1  # 數字部分加 1，即 21
        next_id = f"{prefix}{next_number:02}"  # 將 ID 前綴與新的數字部分結合，並確保數字部分有兩位數，即 'KH21'
    else:
        regions = ["TP", "NT", "TY", "TC", "TN","KH", "YL", "HC", "ML", "CH","NT", "YL", "JY", "PT", "TT","HL", "PH", "KL", "XZ", "CY","KM", "LJ"]
        prefix=regions[region-1]
        next_id = f"{prefix}1"

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO House VALUES (%s, %s, %s, %s, %s)',(next_id, 0,title,region,"888"))
        cursor.execute('INSERT INTO Info  VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)',(next_id,Info['price'],Info['address'],Info['level'],Info['room'],Info['living'],Info['bath'],Info['type'],Info['size'],current_date))
        cursor.execute('INSERT INTO Equipment  VALUES (%s, %s,%s,%s, %s,%s, %s, %s, %s, %s, %s, %s)',(next_id,Equip['sofa'], Equip['tv'], Equip['washer'], Equip['wifi'], Equip['bed'], Equip['refrigerator'], Equip['heater'], Equip['channel4'], Equip['cabinet'], Equip['aircond'], Equip['gas']))
        cursor.execute("INSERT INTO Rdetail VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(next_id,"0",Rdetails['parking'],Rdetails['pet'],Rdetails['cook'],Rdetails['direction'],Rdetails['level'],Rdetails['security'],Rdetails['management'],Rdetails['period'],Rdetails['bus'],Rdetails['train'],Rdetails['mrt'],Rdetails['age']))

    return render(request, "homepage.html")

def account_center(request):
    if 'user' in request.session:
        rows = Member.objects.raw('SELECT * FROM Member WHERE Member.username_id=%s', [request.session['user']])
        print(rows)
        print(rows[0])

        return render(request, "account_center.html",{'row': rows[0]})
    else:#若沒有登錄
        return redirect('login_page')#去homepage這個函數


def testing(request):
    # 获取当前日期

    mId=Member.objects.latest('mId')
    # mId=Member.objects.order_by('-mId').last()
    print(mId.mId)
    # print("当前日期:", current_date)
    if House.objects.filter(hId="HC41").exists():
        print("数据库中存在该数据记录")
    else:
        print("数据库中不存在该数据记录")

    return render(request, "homepage.html")

def search_test(request):
    keyword = request.POST['keyword']

    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.title LIKE %s OR Info.address LIKE %s AND House.hId=Info.hId_id', ['%'+keyword+'%'], ['%'+keyword+'%'])

    return render(request, "house_list.html", {'rows': rows})