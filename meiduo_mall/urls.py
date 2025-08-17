# 总路由
from django.contrib import admin
from django.urls import path,include

from utils.converters import UsernameConverter
from utils.converters import MobileConverter  # 手机注册的路由转换导入包

from django.urls import register_converter

register_converter(UsernameConverter,'username')
register_converter(MobileConverter,'mobile')  # 手机注册规定类型名

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('apps.users.urls')),
    path('', include('apps.areas.urls')),
    path('', include('apps.goods.urls')),
]

