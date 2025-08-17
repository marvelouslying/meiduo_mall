# 用户子路由
from django.urls import path, include
from . import views

urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),
    # 判断手机号是否重复
    path('mobiles/<mobile:mobile>/count/', views.MobileCountView.as_view()),
    # 注册
    path('register/', views.RegisterView.as_view()),
    # 登录
    path('login/', views.LoginView.as_view()),
    # 退出
    path('logout/', views.LogoutView.as_view()),
    # 用户中心
    path('center/', views.CenterView.as_view()),
    path('info/', views.CenterView.as_view()),  # 注意，这里是js代码中
    # 创建地址
    path('addresses/create/', views.CreateAddressView.as_view()),
    # 地址视图
    path('addresses/', views.AddressView.as_view()),
    # 修改和删除地址
    path('addresses/<address_id>/', views.UpdateDestroyAddressView.as_view()),
    # 设置默认地址
    path('addresses/<address_id>/default/',views.DefaultAddressView.as_view()),
    # 修改地址
    path('addresses/<address_id>/title/',views.UpdateTitleAddressView.as_view()),

    path('password/', views.ChangePasswordView.as_view()),
]