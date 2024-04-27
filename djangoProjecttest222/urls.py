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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', my_app.views.homepage),
    path('register/', my_app.views.register),
    path('register/receive/', my_app.views.register_received),
    path('login/', my_app.views.login_page, name='login_page'),
    path('login/login_act/', my_app.views.login_act, name='login_act'),
    path('house_list/',my_app.views.house_list),
    path('house_rent_cont/<str:hId>',my_app.views.house_rent_cont),
    path('upload_page',my_app.views.upload_page),

]
