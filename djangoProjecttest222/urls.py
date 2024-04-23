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
    path('123/',my_app.views.index),
    path('456/678/',my_app.views.getdata),
    path('home/',my_app.views.homepage),
    path('', my_app.views.aboutme),
    path('aboutme/',my_app.views.aboutme),
    path('map/', my_app.views.map),
    path('register/', my_app.views.register),
    path('register/receive/', my_app.views.register_received),
]
