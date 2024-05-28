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

import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox
import logging
from django.views.decorators.csrf import csrf_exempt  # 添加 CSRF 装饰器
# from .face_recognition import recognize_face

import datetime


#引入 Table
from my_app.models import Member, House, Image, Equipment, User, Member, Browse, Review, Rdetail, Favourite, Sdetail,Booking


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
    if 'index' in request.GET:
        index = int(request.GET['index'])
    else:
        index=0

    my_list = ["renewdate", "price", "size"]
    order_by_field = my_list[index]  # 获取列表中的第一个元素作为排序字段

    if 'keyword' in request.POST:
        keyword = request.POST['keyword']

        query = '''
                    SELECT * FROM Info 
                    JOIN House ON Info.hId_id=House.hId 
                    AND House.status=0 
                    AND House.available=1 
                    LEFT OUTER JOIN (
                        SELECT * FROM Favourite WHERE Favourite.mId_id=%s
                    ) f ON f.hId_id=House.hId WHERE Info.address LIKE %s
                    ORDER BY Info.%s;  -- 使用字符串格式化将排序字段替换为变量
                '''

        rows = House.objects.raw(query % (member,'%' + keyword + '%', order_by_field))  # 将变量插入SQL查询中并执行
        # rows = House.objects.raw('''SELECT * FROM Info JOIN House ON Info.hId_id=House.hId AND House.status=0 AND House.available=1 LEFT OUTER JOIN
        #                                 (SELECT * FROM Favourite WHERE Favourite.mId_id=%s) f
        #                             ON f.hId_id=hId WHERE Info.address LIKE %s ;
        #                             ''',(member,'%' + keyword + '%', ))
        numbers = len(list(rows))  # 转换为列表再计数


        return render(request, "house/house_list.html", {'numbers': numbers,'login':login,'rows': rows, 'index': index})

        # 如果沒有search
    else:
        query = '''
            SELECT * FROM Info 
            JOIN House ON Info.hId_id=House.hId 
            AND House.status=0 
            AND House.available=1 
            LEFT OUTER JOIN (
                SELECT * FROM Favourite WHERE Favourite.mId_id=%s
            ) f ON f.hId_id=House.hId 
            ORDER BY Info.%s;  -- 使用字符串格式化将排序字段替换为变量
        '''

        rows = House.objects.raw(query % (member, order_by_field))  # 将变量插入SQL查询中并执行
        # rows = House.objects.raw('''SELECT * FROM Info JOIN House ON Info.hId_id=House.hId AND House.status=0 AND House.available=1 LEFT OUTER JOIN
        #                                         (SELECT * FROM Favourite WHERE Favourite.mId_id=%s) f
        #                                     ON f.hId_id=hId ORDER BY Info.renewdate;
        #                                     ''',(member,))
        numbers = len(list(rows))  # 转换为列表再计数
        return render(request, "house/house_list.html", {'numbers': numbers,'login':login,'rows': rows, 'index': index})

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

    numbers = len(list(review))  # 转换为列表再计数

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
    return render(request, "house/house_rent.html", {"rows":rows[0], "image":image, "equipment":equipment[0], "seller":seller[0],  "details":details[0],"login_people":login_people, "login":login,"review":review,"numbers":numbers})

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
    houses_to_delete.delete()
    return redirect('house_lists')

def upload_page(request):

    if 'user' in request.session and 'mId' in request.session:
        return render(request, "add_renew_delete/upload_page.html")

    else:
        return redirect('/login/')

def add_house(request):
    # del request.session['user']
    current_date = datetime.date.today()
    # House
    region = int(request.POST['region'])
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
        prefix = latest_id.hId[0:2]  # 取得 ID 前綴，即 'KH'
        number_part = int(latest_id.hId[2:])  # 取得數字部分，轉換為整數，即 20
        next_number = number_part + 1  # 數字部分加 1，即 21
        next_id = prefix + str(next_number)  # 将前缀与新的数字部分直接拼接
    else:
        regions = ["TP", "NT", "TY", "TC", "TN", "KH", "YL", "HC", "ML", "CH", "NT", "YL", "JY", "PT", "TT", "HL", "PH",
                   "KL", "XZ", "CY", "KM", "LJ"]
        prefix = regions[region - 1]
        next_id = f"{prefix}1"

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO House VALUES (%s, %s, %s,%s, %s, %s)',(next_id, 0,title,region,member,1))
        cursor.execute('INSERT INTO Info  VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)',(next_id,Info['price'],Info['address'],Info['level'],Info['room'],Info['living'],Info['bath'],Info['type'],current_date,Info['size']))
        cursor.execute('INSERT INTO Equipment  VALUES (%s,%s, %s,%s,%s, %s,%s, %s, %s, %s, %s, %s, %s)',(next_id,Equip['sofa'], Equip['tv'], Equip['washer'], Equip['wifi'], Equip['bed'], Equip['refrigerator'], Equip['heater'], Equip['channel4'], Equip['cabinet'], Equip['aircond'], Equip['gas'],lift))
        cursor.execute("INSERT INTO Rdetail VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(next_id,"0",Rdetails['parking'],Rdetails['pet'],Rdetails['cook'],Rdetails['direction'],Rdetails['level'],Rdetails['security'],Rdetails['management'],Rdetails['period'],Rdetails['bus'],Rdetails['train'],Rdetails['mrt'],Rdetails['age']))

    # 處理圖片上傳+重命名
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

    house = f'/house_sold/{next_id}'
    return redirect(house)

def upload_page_sold(request):

    if 'user' in request.session and 'mId' in request.session:
        return render(request, "add_renew_delete/upload_page_sold.html")

    else:
        return redirect('/login/')

def add_house_sold(request):
    # del request.session['user']
    current_date = datetime.date.today()
    # House
    region = int(request.POST['region'])
    title = request.POST['title']
    # Info
    fields = ['address', 'room', 'bath', 'living', 'size', 'type', 'level', 'price']
    Info = {field: request.POST[field] for field in fields}
    print(Info)

    # Rdetails
    fields = ['parking','direction','level','security','management','period','bus','train','mrt','age']
    Rdetails = {field: request.POST.get(field, '0') for field in fields}
    print(Rdetails)
    # Equipments
    lift=request.POST['lift']
    #member_id
    member = request.session['mId']
    # Count next id
    if(House.objects.filter(region=region)):
        latest_id = House.objects.filter(region=region).latest('hId')
        prefix = latest_id.hId[0:2]  # 取得 ID 前綴，即 'KH'
        number_part = int(latest_id.hId[2:])  # 取得數字部分，轉換為整數，即 20
        next_number = number_part + 1  # 數字部分加 1，即 21
        next_id = prefix + str(next_number)  # 将前缀与新的数字部分直接拼接
    else:
        regions = ["TP", "NT", "TY", "TC", "TN","KH", "YL", "HC", "ML", "CH","NT", "YL", "JY", "PT", "TT","HL", "PH", "KL", "XZ", "CY","KM", "LJ"]
        prefix=regions[region-1]
        next_id = f"{prefix}1"

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO House VALUES (%s, %s, %s,%s, %s, %s)',(next_id, 1,title,region,member,1))
        cursor.execute('INSERT INTO Info  VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)',(next_id,Info['price'],Info['address'],Info['level'],Info['room'],Info['living'],Info['bath'],Info['type'],current_date,Info['size']))
        cursor.execute("INSERT INTO Sdetail VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(next_id,"1",Rdetails['parking'],Rdetails['direction'],Rdetails['level'],Rdetails['age'],Rdetails['security'],Rdetails['management'],Rdetails['bus'],Rdetails['train'],Rdetails['mrt'],lift))

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

    house = f'/house_sold/{next_id}'
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
                       (Info['price'],Info['address'],Info['level'],Info['room'],Info['living'],Info['bath'],Info['type'],current_date,Info['size'],hId))
        cursor.execute('UPDATE Equipment  SET sofa = %s, tv = %s, washer = %s, wifi = %s, bed = %s, refrigerator = %s, heater = %s, channel4 = %s, cabinet = %s, aircond = %s, gas = %s WHERE hId_id = %s',
                       (Equip['sofa'], Equip['tv'], Equip['washer'], Equip['wifi'], Equip['bed'], Equip['refrigerator'], Equip['heater'], Equip['channel4'], Equip['cabinet'], Equip['aircond'], Equip['gas'],hId))
        cursor.execute("UPDATE Rdetail SET parking = %s, pet = %s, cook = %s, direction = %s, level = %s, security = %s, management = %s, period = %s, bus = %s, train = %s, mrt = %s, age = %s WHERE hId_id = %s",
                       (Rdetails['parking'],Rdetails['pet'],Rdetails['cook'],Rdetails['direction'],Rdetails['level'],Rdetails['security'],Rdetails['management'],Rdetails['period'],
                        Rdetails['bus'],Rdetails['train'],Rdetails['mrt'],Rdetails['age'],hId))
    house = f'/house_rent/{hId}'

    return redirect(house)

def edit_page_show_sold(request,hId):

    if 'user' in request.session:
        # 查询数据库，获取对应 hId 的标题数据
        house = House.objects.raw("SELECT * FROM House,Info,Sdetail WHERE House.hId=%s AND House.hId=Info.hId_id AND House.hId=Sdetail.hId_id", [hId])
        img_path = Image.objects.raw("SELECT * FROM Image WHERE Image.hId_id=%s",[hId])
        return render(request, "add_renew_delete/edit_house_sold.html", {'house': house[0], 'img_path': img_path})

    else:
        return redirect('/login/')

def edit_page_update_sold(request,hId):
    current_date = datetime.date.today()
    # House
    region = request.POST['region']
    title = request.POST['title']
    # Info
    fields = ['address', 'room', 'bath', 'living', 'size', 'type', 'level', 'price']
    Info = {field: request.POST[field] for field in fields}
    print(Info)

    #Sdetails
    fields = ['parking','direction','level','security','management','bus','train','mrt','age','lift']
    Rdetails = {field: request.POST.get(field, '0') for field in fields}

    # Image
    images = request.POST.getlist('img_delete')

    # 删除指定路径的文件

    with connection.cursor() as cursor:
        for img_path in images:
            cursor.execute('DELETE FROM Image WHERE path=%s', [img_path])
            file_path = f'my_app/static/img/house/{img_path}'
            os.remove(file_path)

    with connection.cursor() as cursor:
        cursor.execute('UPDATE House SET title = %s, region = %s WHERE hId = %s',(title,region,hId))
        cursor.execute('UPDATE Info SET price = %s, address = %s, level = %s, room = %s, living = %s, bath = %s, type = %s, size = %s, renewdate = %s WHERE hId_id = %s',
                       (Info['price'],Info['address'],Info['level'],Info['room'],Info['living'],Info['bath'],Info['type'],current_date,Info['size'],hId))
        cursor.execute("UPDATE Sdetail SET parking = %s, direction = %s, level = %s, security = %s, management = %s, bus = %s, train = %s, mrt = %s, age = %s, lift=%s WHERE hId_id = %s",
                       (Rdetails['parking'],Rdetails['direction'],Rdetails['level'],Rdetails['security'],Rdetails['management'],
                        Rdetails['bus'],Rdetails['train'],Rdetails['mrt'],Rdetails['age'],Rdetails['lift'],hId))
    house = f'/house_sold/{hId}'

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
        cursor.execute('DELETE FROM Review WHERE review_seq= %s', (review_seq,))
    house = f'/house_rent/{hId}'
    return redirect(house)

def add_favor(request,hId,index):
    latest_favourite_seq = Favourite.objects.aggregate(Max('favourite_seq'))['favourite_seq__max']
    if latest_favourite_seq:
        latest_favourite_seq = latest_favourite_seq + 1
    else:
        latest_favourite_seq = 1
    member = request.session['mId']
    house_rent = f'/house_list/?index={index}'
    house_sold = f'/house_list_sold/?index={index}'
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Favourite VALUES (%s, %s, %s)',(latest_favourite_seq, hId, member))
    status=House.objects.raw('SELECT hId,status FROM House WHERE hId=%s',[hId])
    if status[0].status==0:
        return redirect(house_rent)
    else:
        return redirect(house_sold)

def del_favor(request,favourite_seq,hId,index):

    member = request.session['mId']
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM Favourite WHERE favourite_seq= %s', (favourite_seq,))
    status = House.objects.raw('SELECT hId,status FROM House WHERE hId=%s', [hId])
    house_rent = f'/house_list/?index={index}'
    house_sold = f'/house_list_sold/?index={index}'
    if status[0].status==0:
        return redirect(house_rent)
    else:
        return redirect(house_sold)

def accept_booking(request,booking_seq):
    with connection.cursor() as cursor:
        cursor.execute('UPDATE Booking SET situation=%s WHERE booking_seq=%s',("同意看房",booking_seq))

    return redirect('/account_center/')
def reject_booking(request,booking_seq):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM Booking WHERE booking_seq=%s',(booking_seq,))
    return redirect('/account_center/')

def renew_booking(request,booking_seq):
    latest_sitaution=request.GET['booking_renew']


    with connection.cursor() as cursor:
            cursor.execute('UPDATE Booking SET situation=%s WHERE booking_seq=%s',(latest_sitaution,booking_seq))
            cursor.execute('UPDATE House SET available=1 WHERE hId=(SELECT hId_id FROM Booking WHERE booking_seq=%s)',
                           (booking_seq,))
            if latest_sitaution=="已成交":
                cursor.execute('UPDATE House SET available=0 WHERE hId=(SELECT hId_id FROM Booking WHERE booking_seq=%s)',(booking_seq,))

    return redirect('/account_center/')

def renew_booking_time(request,booking_seq):
    time=request.GET['time']
    date = request.GET['date']

    with connection.cursor() as cursor:
        cursor.execute('UPDATE Booking SET time=%s,date=%s  WHERE booking_seq=%s', (time,date,booking_seq))

    return redirect('/account_center/')

def house_list_sold(request):
    login=0
    if 'user' in request.session and 'mId' in request.session:
        member = request.session['mId']
        login = 1
    else:
        login = 0
        member = "000"

    # 如果有search東西
    if 'index' in request.GET:
        index = int(request.GET['index'])
    else:
        index=0

    my_list = ["renewdate", "price", "size"]
    order_by_field = my_list[index]  # 获取列表中的第一个元素作为排序字段

    if 'keyword' in request.POST:
        keyword = request.POST['keyword']

        query = '''
                            SELECT * FROM Info 
                            JOIN House ON Info.hId_id=House.hId 
                            AND House.status=1 
                            AND House.available=1 
                            LEFT OUTER JOIN (
                                SELECT * FROM Favourite WHERE Favourite.mId_id=%s
                            ) f ON f.hId_id=House.hId WHERE Info.address LIKE %s
                            ORDER BY Info.%s;  -- 使用字符串格式化将排序字段替换为变量
                        '''

        rows = House.objects.raw(query % (member, '%' + keyword + '%', order_by_field))  # 将变量插入SQL查询中并执行
        # rows = House.objects.raw('''SELECT * FROM Info JOIN House ON Info.hId_id=House.hId AND House.status=1 AND House.available=1 LEFT OUTER JOIN
        #                                         (SELECT * FROM Favourite WHERE Favourite.mId_id=%s) f
        #                                     ON f.hId_id=hId WHERE Info.address LIKE %s;
        #                                     ''', (member, '%' + keyword + '%'))
        numbers = len(list(rows))  # 转换为列表再计数

        return render(request, "house/house_list_sold.html", {'numbers': numbers, 'login': login, 'rows': rows, 'index': index})

        # 如果沒有search
    else:
        query = '''
                    SELECT * FROM Info 
                    JOIN House ON Info.hId_id=House.hId 
                    AND House.status=1 
                    AND House.available=1 
                    LEFT OUTER JOIN (
                        SELECT * FROM Favourite WHERE Favourite.mId_id=%s
                    ) f ON f.hId_id=House.hId 
                    ORDER BY Info.%s;  -- 使用字符串格式化将排序字段替换为变量
                '''

        rows = House.objects.raw(query % (member, order_by_field))  # 将变量插入SQL查询中并执行
        # rows = House.objects.raw('''SELECT * FROM Info JOIN House ON Info.hId_id=House.hId AND House.status=1 AND House.available=1 LEFT OUTER JOIN
        #                                                 (SELECT * FROM Favourite WHERE Favourite.mId_id=%s) f
        #                                             ON f.hId_id=hId;
        #                                             ''', [member])
        numbers = len(list(rows))  # 转换为列表再计数
        return render(request, "house/house_list_sold.html", {'numbers': numbers, 'login': login, 'rows': rows})

def house_sold(request, hId):
    # House Data
    rows = House.objects.raw('SELECT * FROM House,Info WHERE House.hId=%s AND House.hId=Info.hId_id', [hId])
    image = Image.objects.raw('SELECT path FROM Image WHERE Image.hId_id=%s', [hId])
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
                      {"rows": rows[0], "image": image, "seller": seller[0],
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
        SELECT * FROM Info JOIN House ON Info.hId_id=House.hId 
            JOIN (SELECT * FROM Favourite WHERE Favourite.mId_id=%s ) f
            ON f.hId_id=hId''',(member,))

    browse = House.objects.raw('''
        SELECT * FROM Info JOIN House ON Info.hId_id=House.hId 
            JOIN (SELECT * FROM Browse WHERE Browse.mId_id=%s) f ON f.hId_id=hId
            LEFT OUTER JOIN Favourite ON Favourite.hId_id=hId  ORDER BY f.browse_seq DESC
            ''',(member,))

    booking_seller = House.objects.raw('''SELECT booking_seq,date,time,hId,title,status,address,mId_id,situation,realname FROM Booking,House,Info,Member
        WHERE Booking.hId_id=House.hId AND House.hId=Info.hId_id AND Member.mId=Booking.customer_id_id
            AND House.mId_id=%s ORDER BY Booking.booking_seq DESC''',[member])

    booking_customer = House.objects.raw('''SELECT booking_seq,date,time,hId,title,status,address,mId_id,situation FROM Booking,House,Info
            WHERE Booking.hId_id=House.hId 
            AND House.hId=Info.hId_id 
            AND Booking.customer_id_id=%s
            AND Booking.situation != %s
            ORDER BY Booking.booking_seq DESC''', (member, "已成交"))

    member_detail = User.objects.raw('SELECT * FROM Member,User WHERE Member.username_id=User.username AND Member.mId=%s',[member])

    # print(booking_seller)
    # print(booking_seller[0].booking_seq)
    return render(request, "homepage_login_account/account_center.html", {'login': login, 'rows': Favourite, 'browse':browse, 'booking_seller':booking_seller,"booking_customer":booking_customer,"member_detail":member_detail})

    # return render(request, "homepage_login_account/account_center.html", {'login': login, 'rows': Favourite, 'browse':browse})

def city_filter(request, city_id, status):
    if 'user' in request.session and 'mId' in request.session :
        login=1
    else:
        login=0

    if status==0:
        rows = House.objects.raw(
            'SELECT * FROM House,Info WHERE House.region=%s AND House.hId=Info.hId_id AND House.status=0 AND House.available=1',
            [city_id])
        return render(request, "house/house_list.html", {'numbers': len(rows), 'login': login, 'rows': rows})
    else:
        rows = House.objects.raw(
            'SELECT * FROM House,Info WHERE House.region=%s AND House.hId=Info.hId_id  AND House.status=1 AND House.available=1',
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
        cursor.execute('INSERT INTO Booking VALUES (%s, %s, %s, %s, %s, %s)',
                       (latest_booking_seq, date, time, member, hId, "未確認"))

    house = f'/house_rent/{hId}'
    return redirect(house)

def delete_browse(request):
    mId = request.session['mId']

    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM Browse WHERE mId_id=%s', [mId])

    return redirect('/account_center/')


<<<<<<< Updated upstream
def update_user_detail(request):
    mId = request.session['mId']
    phone = request.POST['phone']
    email = request.POST['email']
    username = request.POST['username']
    gender = request.POST['gender']
    with connection.cursor() as cursor:
        cursor.execute('UPDATE Member SET username_id=%s,gender=%s,phone=%s,email=%s WHERE mId=%s',(username,gender,phone,email,mId))

    return redirect('/account_center/')

def update_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        # 检查用户输入的旧密码是否正确
        if request.user.check_password(old_password):
            # 设置新密码并保存
            request.user.set_password(new_password)
            request.user.save()

            # 更新会话中的用户身份验证哈希以防止用户被注销
            update_session_auth_hash(request, request.user)

            # 重定向到成功页面或者给出成功消息
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password_updated_successfully')  # 替换为你的成功页面URL名称或路径
        else:
            # 如果旧密码不正确，显示错误消息
            messages.error(request, 'Your old password is incorrect.')
            return redirect('change_password')  # 替换为你的修改密码页面URL名称或路径

        # 如果是 GET 请求，返回修改密码页面
    return render(request, 'change_password.html')
def face_recognize_html(request):
    return render(request, 'face_recognize.html')

logger = logging.getLogger(__name__)
@csrf_exempt
def recognize(request):
    try:
        recognized_name = recognize_face()
        if recognized_name:
            message = "Hello, super manager"
            alert = True
        else:
            message = "Face not recognized"
            alert = False
        return JsonResponse({'message': message, 'alert': alert})
    except Exception as e:
        # 捕获并记录异常信息
        print(f"Error during face recognition: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def recognize_face():
    try:
        # 加载模型文件
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("C:/Users/YOYOBILL/Desktop/Database-Project1122/my_app/template/trainer.yml")
        face_cascade_Path = "C:/Users/YOYOBILL/Desktop/Database-Project1122/my_app/template/haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(face_cascade_Path)

        # 加载姓名数据
        with open('C:/Users/YOYOBILL/Desktop/Database-Project1122/my_app/template/names.json', 'r') as fs:
            names = json.load(fs)
            names = list(names.values())

        cam = cv2.VideoCapture(0)
        cam.set(3, 640)
        cam.set(4, 480)
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)

        if not cam.isOpened():
            raise Exception("Could not open video stream from camera.")

        stop_program = False
        recognized_name = None
        detection_start_time = {}
        current_detected_id = None
        current_detection_start = None

        while True:
            ret, img = cam.read()
            if not ret:
                raise Exception("Failed to capture image")

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=8,
                minSize=(int(minW), int(minH)),
            )
            current_time = time.time()
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                if confidence >= 90:
                    try:
                        name = names[id]
                        confidence_text = "  {0}%".format(round(confidence))
                    except IndexError as e:
                        name = "Who are you?"
                        confidence_text = "N/A"
                else:
                    name = "Who are you?"
                    confidence_text = "N/A"
                display_name = "got it" if name != "Who are you?" else name
                cv2.putText(img, display_name, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(img, confidence_text, (x + 5, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)
                if name != "Who are you?":
                    if current_detected_id == id:
                        if current_time - current_detection_start >= 3:
                            recognized_name = name
                            stop_program = True
                            break
                    else:
                        current_detected_id = id
                        current_detection_start = current_time
                else:
                    current_detected_id = None
                    current_detection_start = None
            cv2.imshow('camera', img)
            k = cv2.waitKey(10) & 0xff
            if k == 27 or stop_program:
                break

        cam.release()
        cv2.destroyAllWindows()

        if recognized_name:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("Alert", "hello, super manager")

        return recognized_name
    except Exception as e:
        print(f"Error in recognize_face: {str(e)}")
        raise
>>>>>>> Stashed changes
