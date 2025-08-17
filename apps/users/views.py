from django.shortcuts import render
from django.views import View
from apps.users.models import User, Address
from django.http import JsonResponse
import json, re


# 判断重复视图
class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


# 判断重复手机号
class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


# 注册视图
class RegisterView(View):
    """用户注册"""

    def post(self, request):
        """
        实现用户注册
        :param request: 请求对象
        :return: 注册结果
        """
        # 1. 接收请求（POST------JSON）
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)

        # 2. 获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')

        # 3. 验证数据
        #     3.1 用户名，密码，确认密码，手机号，是否同意协议 都要有
        # all([xxx,xxx,xxx])
        # all里的元素 只要是 None,False
        # all 就返回False，否则返回True
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 3.2 用户名满足规则，用户名不能重复
        if not re.match('[a-zA-Z_-]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足规则'})
        # 3.3 密码满足规则
        #     3.4 确认密码和密码要一致
        #     3.5 手机号满足规则，手机号也不能重复
        #     3.6 需要同意协议
        '''
        数据入库只需要存储一遍即可
        数据入库代码: user=User(username=username.password=password,moble=mobile))
        '''
        # 4. 数据入库
        # user=User(username=username,password=password,moble=mobile)
        # user.save()

        # User.objects.create(username=username, password=password, mobile=mobile)
        # 以上2中方式，都是可以数据入库的
        # 但是 有一个问题 密码没有加密

        # 密码就加密(用系统提供的create_user方法，可以实现密码的加密。)
        # user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 保存注册数据
        from sqlite3 import DatabaseError
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return JsonResponse({'code': 400, 'errmsg': '注册失败!'})

        # 实现状态保持
        # 系统（Django）为我们提供了 状态保持的方法
        from django.contrib.auth import login
        # request, user,
        # 状态保持 -- 登录用户的状态保持
        # user 已经登录的用户信息
        login(request, user)

        # 响应注册结果
        return JsonResponse({'code': 0, 'errmsg': '注册成功!'})

        # 5. 返回响应
        # return JsonResponse({'code': 0, 'errmsg': 'ok'})


# 用户登录
from django.contrib.auth import authenticate, login


class LoginView(View):
    """用户名登录"""

    def post(self, request):
        """
        实现登录逻辑
        :param request: 请求对象
        :return: 登录结果
        """
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        remembered = dict.get('remembered')

        # 2.校验(整体 + 单个)
        if not all([username, password]):
            return JsonResponse({'code': 400,
                                 'errmsg': '缺少必传参数'})
            # 根据正则表达式确定 我们是根据手机号查询 还是 根据用户名查询
            # USERNAME_FIELD 我们可以根据 修改 User. USERNAME_FIELD 字段
            # 来影响authenticate 的查询
            # authenticate 就是根据 USERNAME_FIELD 来查询
            if re.match('1[3-9]\d{9}', username):
                User.USERNAME_FIELD = 'mobile'
            else:
                User.USERNAME_FIELD = 'username'

        # 3.验证是否能够登录
        user = authenticate(username=username,
                            password=password)

        # 判断是否为空,如果为空,返回
        if user is None:
            return JsonResponse({'code': 400,
                                 'errmsg': '用户名或者密码错误'})

        # 4.状态保持
        login(request, user)

        # 5.判断是否记住用户
        if remembered != True:
            # 7.如果没有记住: 关闭立刻失效
            request.session.set_expiry(0)
        else:
            # 6.如果记住:  设置为两周有效
            request.session.set_expiry(None)

        # 显示用户中心的代码
        response = JsonResponse({'code': 0, 'errmsg': 'OK'})
        response.set_cookie('username', user.username)
        return response


# 退出登录
from django.contrib.auth import logout


class LogoutView(View):
    """退出登录"""

    def delete(self, request):
        """实现退出登录逻辑"""
        # 清理session
        logout(request)
        # 退出登录，重定向到登录页
        response = JsonResponse({'code': 0,
                                 'errmsg': 'ok'})
        # 退出登录时清除cookie中的username
        response.delete_cookie('username')

        return response


# 用户中心，必须先登录然后才能访问
from utils.views import LoginRequiredJSONMixin


class CenterView(LoginRequiredJSONMixin, View):
    def get(self, request):
        # # 获取界面需要的数据,进行拼接
        info_data = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': info_data})


from django import http
# class EmailView(View):
#     """添加邮箱"""
#
#     def put(self, request):
#         """实现添加邮箱逻辑"""
#         # 接收参数
#         json_dict = json.loads(request.body.decode())
#         email = json_dict.get('email')
#
#         # 校验参数
#         if not email:
#             return http.JsonResponse({'code': 400,
#                                       'errmsg': '缺少email参数'})
#         if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return http.JsonResponse({'code': 400,
#                                       'errmsg': '参数email有误'})
#
#
#             # 赋值email字段
#         try:
#             request.user.email = email
#             request.user.save()
#         except Exception as e:
#             logger.error(e)
#             return http.JsonResponse({'code': 400, 'errmsg': '添加邮箱失败'})
#
#         # 响应添加邮箱结果
#         return http.JsonResponse({'code':0, 'errmsg': '添加邮箱成功'})


from django.http import HttpResponseBadRequest
from . import models
import logging


class CreateAddressView(LoginRequiredJSONMixin, View):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""
        # 判断是否超过地址上限：最多20个
        # Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()
        if count >= 20:
            return JsonResponse({'code': 1000, 'errmsg': '超过地址数量上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseBadRequest('参数email有误')

        # 保存地址信息
        try:
            address = models.Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger = logging.getLogger('Django')
            logger.error(e)
            return JsonResponse({'code': 1001, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return JsonResponse({'code': 0, 'errmsg': '新增地址成功', 'address': address_dict})


# from models import Address # 这一行不能加
class AddressView(View):
    """用户收货地址"""

    def get(self, request):
        """提供地址管理界面
        """
        # 获取所有的地址:
        addresses = Address.objects.filter(user=request.user,
                                           is_deleted=False)

        # 创建空的列表
        address_dict_list = []
        # 遍历
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }

            # 将默认地址移动到最前面
            default_address = request.user.default_address
            if default_address.id == address.id:
                # 查询集 addresses 没有 insert 方法
                address_dict_list.insert(0, address_dict)
            else:
                address_dict_list.append(address_dict)

        default_id = request.user.default_address_id

        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'addresses': address_dict_list,
                             'default_address_id': default_id})


# """修改和删除地址"""
class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.JsonResponse({'code': 400,
                                          'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.JsonResponse({'code': 400,
                                          'errmsg': '参数email有误'})

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            # logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': 0, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        try:
            # 查询要删除的地址
            address = models.Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger = logging.getLogger('Django')
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return JsonResponse({'code': 0, 'errmsg': '删除地址成功'})

# 设置默认地址后端逻辑实现
class DefaultAddressView(LoginRequiredJSONMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """设置默认地址"""
        try:
            # 接收参数,查询地址
            address = models.Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger = logging.getLogger('Django')
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '设置默认地址失败'})

        # 响应设置默认地址结果
        return JsonResponse({'code': 0, 'errmsg': '设置默认地址成功'})


# 修改地址标题后端逻辑实现
class UpdateTitleAddressView(LoginRequiredJSONMixin, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = models.Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger = logging.getLogger('Django')
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return JsonResponse({'code': 0, 'errmsg': '设置地址标题成功'})


# 修改密码后端逻辑
from django.contrib.auth.mixins import LoginRequiredMixin

class ChangePasswordView(LoginRequiredMixin, View):
      # """修改密码"""
  def put(self, request):
        """实现修改密码逻辑"""
        # 接收参数
        dict = json.loads(request.body.decode())
        old_password = dict.get('old_password')
        new_password = dict.get('new_password')
        new_password2 = dict.get('new_password2')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
           return JsonResponse({'code':400,
                                     'errmsg':'缺少必传参数'})


        result = request.user.check_password(old_password)
        if not result:
            return JsonResponse({'code':400,
                                      'errmsg':'原始密码不正确'})

        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return JsonResponse({'code':400,
                                      'errmsg':'密码最少8位,最长20位'})

        if new_password != new_password2:
            return JsonResponse({'code':400,
                                      'errmsg':'两次输入密码不一致'})

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:

            return JsonResponse({'code':400,
                                      'errmsg':'修改密码失败'})

        # 清理状态保持信息
        logout(request)

        response = JsonResponse({'code':0,
                                      'errmsg':'ok'})

        response.delete_cookie('username')

        # # 响应密码修改结果：重定向到登录界面
        return response
