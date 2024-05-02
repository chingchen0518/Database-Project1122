"""
URL configuration for djangoProjecttest222 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import my_app.views
# from .views import YourModelDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', my_app.views.homepage, name='homepage'),
    path('', my_app.views.house_list, name='homepage'),

    # 註冊登錄退出
    path('register/', my_app.views.register,name="register"),
    path('register/receive/', my_app.views.register_received,name='register_act'),
    path('login/', my_app.views.login_page, name='login_page'),
    path('login/login_act/', my_app.views.login_act, name='login_act'),
    path('logout/', my_app.views.logout, name='logout'),

    #房屋顯示
    path('house_list/',my_app.views.house_list, name='house_lists'),
    path('house_rent_cont/<str:hId>',my_app.views.house_rent_cont),

    #新增刪除
    path('upload_page',my_app.views.upload_page),
    path('upload_page/add_house',my_app.views.add_house, name='add_house'),
    path('delete/<str:hId>/', my_app.views.HouseDeleteView.as_view(),name='delete_house'),

    #用戶中心
    path('account_center/',my_app.views.account_center,name="account_center"),

    #沒用的東西
    path('testing/',my_app.views.imgup,name="testing"),

    #搜尋測試
    path('house_list/search_test/', my_app.views.search_test, name='search_test'),

    #編輯
    path('edit_page/<str:hId>/',my_app.views.edit_page_show),
    path('edit_page/edit_house/<str:hId>/',my_app.views.edit_page_update, name='edit_house'),

    #Templates
    path('houses/<str:hId>',my_app.views.showhomes,name='house_show'),
]
