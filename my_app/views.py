from django.shortcuts import HttpResponse,render,redirect
import json
from django.http import JsonResponse
from django.db import connection
from django.db.models import Min
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
import os
from django.db.models import Count


import datetime


#引入 Table
from my_app.models import Member, House, Image, Equipment, User, Member, Browse, Review, Rdetail, Favourite, Sdetail


#endregion 引入 Table結束

# region Part 1：首頁
def homepage(request):
    if 'user' in request.session:
        return render(request, "homepage_login_account/homepage.html",{'user':request.session['user']})
    return render(request,"homepage_login_account/homepage.html",{'user':0})

#endregion

#region Part 2：用戶、注冊、登錄
def register(request):
    if 'user' in request.session:
        return redirect('homepage')

    else:
        return render(request,"homepage_login_account/register.html")

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
    request.session['mId'] = mId
    return redirect('homepage')

def login_page(request):
    if 'user' in request.session and 'mId' in request.session:
        return redirect('homepage')

    else:
        return render(request,"homepage_login_account/login.html")

def login_act(request):
    username = request.POST['username']
    pwd = request.POST['password']

    user = User.objects.filter(username=username)
    if user:
        if user[0].password==pwd:
            request.session['user'] = username
            member = Member.objects.raw('SELECT mId FROM Member,User WHERE Member.username_id=User.username AND Member.username_id=%s',[username])
            request.session['mId'] = member[0].mId
            return redirect("homepage")
        else:
            return HttpResponse("Wrong username or password")
            return redirect('/login/')

def logout(request):
    del request.session['user']
    del request.session['mId']
    return redirect("homepage")

def account_center2(request):
    if 'user' in request.session:
        rows = Member.objects.raw('SELECT * FROM Member WHERE Member.username_id=%s', [request.session['user']])
        print(rows)
        print(rows[0])

        return render(request, "homepage_login_account/account_center2.html", {'row': rows[0]})
    else:#若沒有登錄
        return redirect('login_page')#去login_page這個函數



#endregion

#region Part 3：房屋顯示相關（包括search）
def house_list(request):
    login=0
    if 'user' in request.session and 'mId' in request.session :
        member = request.session['mId']
        login=1
    else:
        login=0
        member="000"

    # 如果有search東西


    if 'keyword' in request.POST:
        keyword = request.POST['keyword']

       
        rows = House.objects.raw('''SELECT * FROM Info JOIN House ON Info.hId_id=House.hId AND House.status=0 LEFT OUTER JOIN
                                        (SELECT * FROM Favourite WHERE Favourite.mId_id=%s) f
                                    ON f.hId_id=hId WHERE Info.address LIKE %s;
                                    ''',(member,'%' + keyword + '%'))
        numbers = len(list(rows))  # 转换为列表再计数


        return render(request, "house/house_list.html", {'numbers': numbers,'login':login,'rows': rows})

        # 如果沒有search
    else:
        
        rows = House.objects.raw('''SELECT * FROM Info JOIN House ON Info.hId_id=House.hId AND House.status=0 LEFT OUTER JOIN
                                                (SELECT * FROM Favourite WHERE Favourite.mId_id=%s) f
                                            ON f.hId_id=hId;
                                            ''',[member])
        numbers = len(list(rows))  # 转换为列表再计数
        return render(request, "house/house_list.html", {'numbers': numbers,'login':login,'rows': rows})

def house_rent_cont(request,hId):
    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId=%s AND House.hId=Info.hId_id', [hId])
    image = Image.objects.raw('SELECT path FROM Image WHERE Image.hId_id=%s', [hId])
    equipment = Equipment.objects.raw('SELECT * FROM Equipment WHERE Equipment.hId_id=%s', [hId])

    return render(request, "house_rent_cont.html",{'row': rows[0],'images':image,'equipment':equipment[0]})

def house_rent(request,hId):
    # House Data
    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId=%s AND House.hId=Info.hId_id', [hId])
    image = Image.objects.raw('SELECT path FROM Image WHERE Image.hId_id=%s', [hId])
    equipment = Equipment.objects.raw('SELECT * FROM Equipment WHERE Equipment.hId_id=%s', [hId])
    seller = Member.objects.raw('SELECT * FROM Member JOIN House ON House.mId_id=Member.mId WHERE House.hId=%s', [hId])
    details = Rdetail.objects.raw('SELECT * FROM Rdetail WHERE hId_id=%s', (hId,))

    # Review Data
    review = Review.objects.raw('SELECT review_seq,text,attitude,environment,facilities,realname FROM Review,Member WHERE Review.hId_id=%s AND Review.mId_id = Member.mId',[hId])

    if 'mId' in request.session and 'user' in request.session:
        login_people=request.session['mId']
        login=1

        # 查看這個用戶有沒有瀏覽過這一筆了,如果瀏覽過就刪除再插入，否則直接插入
        history = Browse.objects.filter(hId_id=hId, mId_id=request.session['mId'])
        if history.exists():
            history.delete()

        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Browse(hId_id,mId_id) VALUES (%s, %s)', (hId,request.session['mId']))

    else:
        login=0
        login_people="0000"
    # print(login)
    return render(request, "house/house_rent.html", {"rows":rows[0], "image":image, "equipment":equipment[0], "seller":seller[0],  "details":details[0],"login_people":login_people, "login":login,"review":review})

def search_test(request):
    keyword = request.POST['keyword']

    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.title LIKE %s OR Info.address LIKE %s AND House.hId=Info.hId_id', ['%'+keyword+'%'], ['%'+keyword+'%'])

    return render(request, "house_list.html", {'rows': rows})



#endregion

#region Part 4：新增、刪除、修改
def delete_house(request,hId):
    image_paths = Image.objects.raw('SELECT path FROM Image WHERE hId_id=%s', [hId])

    # Delete the actual image from server
    for img_path in image_paths:
        file_path = f'my_app/static/img/house/{img_path.path}'
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Delete the house
    houses_to_delete = House.objects.filter(hId=hId)

    return redirect('house_lists')

# class HouseDeleteView(DeleteView):
#     model = House
#     success_url = reverse_lazy("house_lists")
#     template_name = 'add_renew_delete/delete.html' #之後加一個取消
#     pk_url_kwarg = 'hId' #告訴他用url中的哪個東西作爲primary_key
#
#     def delete(self, request, *args, **kwargs):
#         # 获取即将删除的对象
#         hId = kwargs.get(self.pk_url_kwarg)
#
#         image_paths=Image.objects.raw('SELECT path FROM Image WHERE hId=%s', [hId])
#         print("satu dua tiga")
#         print(image_paths)
#
#         for img_path in image_paths:
#             file_path = f'my_app/static/img/house/{img_path}'
#             os.remove(file_path)
#
#         response = super().delete(request, *args, **kwargs)
#         return response


def upload_page(request):

    if 'user' in request.session and 'mId' in request.session:
        return render(request, "add_renew_delete/upload_page.html")

    else:
        return redirect('/login/')

def add_house(request):
    # del request.session['user']
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
    lift=request.POST['lift']
    #member_id
    member = request.session['mId']
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
        cursor.execute('INSERT INTO House VALUES (%s, %s, %s,%s, %s, %s)',(next_id, 0,title,region,member,1))
        cursor.execute('INSERT INTO Info  VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)',(next_id,Info['price'],Info['address'],Info['level'],Info['room'],Info['living'],Info['bath'],Info['type'],Info['size'],current_date))
        cursor.execute('INSERT INTO Equipment  VALUES (%s,%s, %s,%s,%s, %s,%s, %s, %s, %s, %s, %s, %s)',(next_id,Equip['sofa'], Equip['tv'], Equip['washer'], Equip['wifi'], Equip['bed'], Equip['refrigerator'], Equip['heater'], Equip['channel4'], Equip['cabinet'], Equip['aircond'], Equip['gas'],lift))
        cursor.execute("INSERT INTO Rdetail VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(next_id,"0",Rdetails['parking'],Rdetails['pet'],Rdetails['cook'],Rdetails['direction'],Rdetails['level'],Rdetails['security'],Rdetails['management'],Rdetails['period'],Rdetails['bus'],Rdetails['train'],Rdetails['mrt'],Rdetails['age']))

    # 處理圖片上傳+重命名
    if request.method == 'POST' and request.FILES.getlist('images'):
        files = request.FILES.getlist('images')
        i=1
        for image in files:
            file_extension = os.path.splitext(image.name)[1].lower()
            next_path=f'{next_id}-{i}{file_extension}'
            image_path = os.path.join('my_app/static/img/house/',next_path)
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO Image VALUES (%s, %s)',(next_id,next_path))
            i=i+1

    house = f'/house_rent/{next_id}'
    return redirect(house)

def edit_page_show(request,hId):

    if 'user' in request.session:
        # 查询数据库，获取对应 hId 的标题数据
        house = House.objects.raw("SELECT * FROM House,Info,Equipment,Rdetail WHERE House.hId=%s AND House.hId=Info.hId_id AND House.hId=Equipment.hId_id AND House.hId=Rdetail.hId_id", [hId])
        img_path = Image.objects.raw("SELECT * FROM Image WHERE Image.hId_id=%s",[hId])
        return render(request, "add_renew_delete/edit_house.html", {'house': house[0], 'img_path': img_path})

    else:
        return redirect('/login/')

def edit_page_update(request,hId):
    current_date = datetime.date.today()
    # House
    region = request.POST['region']
    title = request.POST['title']
    # Info
    fields = ['address', 'room', 'bath', 'living', 'size', 'type', 'level', 'price']
    Info = {field: request.POST[field] for field in fields}
    print(Info)

    #Rdetails
    fields = ['parking','pet','cook','direction','level','security','management','period','bus','train','mrt','age']
    Rdetails = {field: request.POST.get(field, '0') for field in fields}
    print(Rdetails)

    #Equipments
    fields = ['sofa', 'tv', 'washer', 'wifi', 'bed', 'refrigerator', 'heater', 'channel4', 'cabinet', 'aircond', 'gas']
    Equip = {field: request.POST.get(field, '0') for field in fields}

    # Image
    images = request.POST.getlist('img_delete')

    # 删除指定路径的文件

    with connection.cursor() as cursor:
        for img_path in images:
            cursor.execute('DELETE FROM Image WHERE path=%s', [img_path])
            file_path = f'my_app/static/img/house/{img_path}'
            os.remove(file_path)

    with connection.cursor() as cursor:
        cursor.execute('UPDATE House SET  title = %s, region = %s WHERE hId = %s',(title,region,hId))
        cursor.execute('UPDATE Info  SET price = %s, address = %s, level = %s, room = %s, living = %s, bath = %s, type = %s, size = %s, renewdate = %s WHERE hId_id = %s',
                       (Info['price'],Info['address'],Info['level'],Info['room'],Info['living'],Info['bath'],Info['type'],Info['size'],current_date,hId))
        cursor.execute('UPDATE Equipment  SET sofa = %s, tv = %s, washer = %s, wifi = %s, bed = %s, refrigerator = %s, heater = %s, channel4 = %s, cabinet = %s, aircond = %s, gas = %s WHERE hId_id = %s',
                       (Equip['sofa'], Equip['tv'], Equip['washer'], Equip['wifi'], Equip['bed'], Equip['refrigerator'], Equip['heater'], Equip['channel4'], Equip['cabinet'], Equip['aircond'], Equip['gas'],hId))
        cursor.execute("UPDATE Rdetail SET parking = %s, pet = %s, cook = %s, direction = %s, level = %s, security = %s, management = %s, period = %s, bus = %s, train = %s, mrt = %s, age = %s WHERE hId_id = %s",
                       (Rdetails['parking'],Rdetails['pet'],Rdetails['cook'],Rdetails['direction'],Rdetails['level'],Rdetails['security'],Rdetails['management'],Rdetails['period'],
                        Rdetails['bus'],Rdetails['train'],Rdetails['mrt'],Rdetails['age'],hId))
    house = f'/house_rent/{hId}'

    return redirect(house)

def add_comment(request,hId):
    message = request.POST['comment_message']
    environment = request.POST['comment_environment']
    attitude = request.POST['comment_attitude']
    facilities = request.POST['comment_facilities']

    print("=-======================")
    print(message)
    print(environment)

    member = request.session['mId']

    latest_review_seq = Review.objects.aggregate(Max('review_seq'))['review_seq__max']
    if latest_review_seq:
        latest_review_seq=latest_review_seq+1
    else:
        latest_review_seq = 1
    #
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Review VALUES (%s, %s, %s, %s, %s, %s, %s)', (latest_review_seq, message, environment, attitude, facilities, hId, member))

    house = f'/house_rent/{hId}'
    return redirect(house)
#endregion

def testing(request):
    # 获取当前日期

    images=request.POST.getlist('images')
    with connection.cursor() as cursor:
        for img_path in images:
            cursor.execute('DELETE FROM Image WHERE path=%s',[img_path])

    # print(imag[0])
    # print(imag[1])
    # mId=Member.objects.latest('mId')
    # # mId=Member.objects.order_by('-mId').last()
    # print(mId.mId)
    # # print("当前日期:", current_date)
    # if House.objects.filter(hId="HC41").exists():
    #     print("数据库中存在该数据记录")
    # else:
    #     print("数据库中不存在该数据记录")

    return render(request, "upload_image.html")

# class Personnel(models.Model):
#     photos = models.ImageField(max_length=255, blank=True, null=True)


# def infoUpload(request):
#     if request.POST:
#
#         img_file = request.FILES.get("image")
#         img_name = 'test.jpg'
#
#         f = open(os.path.join('path/', img_name), 'wb')
#         for chunk in img_file.chunks(chunk_size=1024):
#             f.write(chunk)
#
#     return HttpResponseRedirect('/visit/upload')

def image_upload(request):
    # return render(request, "elements/comment.html")
    return render(request, "upload_image.html")

def upload_image(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        files = request.FILES.getlist('images')
        for image in files:
            image_path = os.path.join('my_app/static/img/temp/', image.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
        return HttpResponse('Images uploaded successfully!')
    return render(request, 'upload_image.html')


# def map(request):
#     return render(request,"map.html")
# from django.shortcuts import render


# from .forms import ImageUploadForm
# def imgup(request):
#     if request.method == 'POST':
#         form = ImageUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             images = request.FILES.getlist('images')
#             for image in images:
#                 # 处理每个上传的图片
#                 handle_uploaded_image(image, '/path/to/destination/folder/')
#             return HttpResponse('上传成功！')
#     else:
#         form = ImageUploadForm()
#     return render(request, 'testimage.html', {'form': form})
#

def delete_comment(request,hId,review_seq):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM Review WHERE review_seq= %s', (review_seq))
    house = f'/house_rent/{hId}'
    return redirect(house)

# def my_view(request):
#     if request.method == 'POST':
#         request.session['button_clicked'] = True
#         return redirect('my_view')  # 重定向到相同视图以更新页面
#
#     button_clicked = request.session.get('button_clicked', False)
#     return render(request, 'my_template.html', {'button_clicked': button_clicked})

def add_favor(request,hId):
    latest_favourite_seq = Favourite.objects.aggregate(Max('favourite_seq'))['favourite_seq__max']
    if latest_favourite_seq:
        latest_favourite_seq = latest_favourite_seq + 1
    else:
        latest_favourite_seq = 1
    member = request.session['mId']
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Favourite VALUES (%s, %s, %s)',(latest_favourite_seq, hId, member))

    return redirect('/house_list/')

def del_favor(request,favourite_seq):

    member = request.session['mId']
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM Favourite WHERE favourite_seq= %s', (favourite_seq,))
    
    return redirect('/house_list/')

def house_list_sold(request):
    login=0
    if 'user' in request.session and 'mId' in request.session :
        login=1
    else:
        login=0

    # 如果有search東西
    # member = request.session['mId']
    if 'keyword' in request.POST:
        keyword = request.POST['keyword']

        rows = House.objects.raw('SELECT * FROM House,Info WHERE Info.address LIKE %s AND House.hId=Info.hId_id  AND House.status=1',
                                 ['%' + keyword + '%'])

        return render(request, "house/house_list_sold.html", {'numbers': len(rows),'login':login,'rows': rows})

        # 如果沒有search
    else:
        rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId=Info.hId_id AND House.status=1')
        

        return render(request, "house/house_list_sold.html", {'numbers': len(rows),'login':login,'rows': rows})

def house_sold(request, hId):
    # House Data
    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId=%s AND House.hId=Info.hId_id', [hId])
    image = Image.objects.raw('SELECT path FROM Image WHERE Image.hId_id=%s', [hId])
    equipment = Equipment.objects.raw('SELECT * FROM Equipment WHERE Equipment.hId_id=%s', [hId])
    seller = Member.objects.raw('SELECT * FROM Member JOIN House ON House.mId_id=Member.mId WHERE House.hId=%s',
                                [hId])
    details = Sdetail.objects.raw('SELECT * FROM Sdetail WHERE hId_id=%s', (hId,))

    # Review Data
    review = Review.objects.raw('SELECT review_seq,text,attitude,environment,facilities,realname FROM Review,Member WHERE Review.hId_id=%s AND Review.mId_id = Member.mId',[hId])

    if 'mId' in request.session and 'user' in request.session:
            login_people = request.session['mId']
            login = 1

            # 查看這個用戶有沒有瀏覽過這一筆了,如果瀏覽過就刪除再插入，否則直接插入
            history = Browse.objects.filter(hId_id=hId, mId_id=request.session['mId'])
            if history.exists():
                history.delete()

            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO Browse(hId_id,mId_id) VALUES (%s, %s)', (hId, request.session['mId']))

    else:
            login = 0
            login_people = "0000"
        # print(login)
    return render(request, "house/house_sold.html",
                      {"rows": rows[0], "image": image, "equipment": equipment[0], "seller": seller[0],
                       "details": details[0], "login_people": login_people, "login": login, "review": review})

def account_center(request):
    login = 0
    if 'user' in request.session and 'mId' in request.session:
        login = 1
        member = request.session['mId']
    else:
        login = 0
        member = 0000

    Favourite = House.objects.raw('''
        SELECT * FROM Info JOIN House ON Info.hId_id=House.hId AND House.status=0 
            JOIN (SELECT * FROM Favourite WHERE Favourite.mId_id=%s ) f
            ON f.hId_id=hId''',(member,))

    browse = House.objects.raw('''
        SELECT * FROM Info JOIN House ON Info.hId_id=House.hId AND House.status=0 
            JOIN (SELECT * FROM Browse WHERE Browse.mId_id=%s ) f ON f.hId_id=hId
            LEFT OUTER JOIN Favourite ON Favourite.hId_id=hId 
            ''',(member,))

    return render(request, "homepage_login_account/account_center.html", {'login': login, 'rows': Favourite, 'browse':browse})

def city_filter(request, city_id, status):
    if 'user' in request.session and 'mId' in request.session :
        login=1
    else:
        login=0

    if status==0:
        rows = House.objects.raw(
            'SELECT * FROM House,Info WHERE House.region=%s AND House.hId=Info.hId_id AND House.status=0',
            [city_id])
        return render(request, "house/house_list.html", {'numbers': len(rows), 'login': login, 'rows': rows})
    else:
        rows = House.objects.raw(
            'SELECT * FROM House,Info WHERE House.region=%s AND House.hId=Info.hId_id  AND House.status=1',
            [city_id])
        return render(request, "house/house_list_sold.html", {'numbers': len(rows),'login':login,'rows': rows})

def add_appointment(request,hId):
    date = request.POST['date']
    time = request.POST['time']
    member = request.session['mId']

    latest_booking_seq = Booking.objects.aggregate(Max('booking_seq'))['booking_seq__max']
    if latest_booking_seq:
        latest_booking_seq = latest_booking_seq + 1
    else:
        latest_booking_seq = 1
    #
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Booking VALUES (%s, %s, %s, %s, %s)',
                       (latest_booking_seq, date, time, member, hId))

    house = f'/house_rent/{hId}'
    return redirect(house)