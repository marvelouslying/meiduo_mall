# 用户子路由
from django.urls import path, include
from . import views

urlpatterns = [
    path('index/', views.IndexView.as_view()),
    path('list/<category_id>/skus/',views.ListView.as_view()),
    path('hot/<category_id>/',views.HotGoodsView.as_view()),
]