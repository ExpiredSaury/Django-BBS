# views.py
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from app01.myforms import MyRegForm
from app01 import models
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth


# 注册功能
def register(request):
    # 生成一个空对象
    form_obj = MyRegForm()
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        # 校验数据是否合法
        form_obj = MyRegForm(request.POST)
        # 判断数据是否合法
        if form_obj.is_valid():

            # print(form_obj.cleaned_data) #4个键值，多传的键值不要
            clean_data = form_obj.cleaned_data  # 将校验通过的数据字典赋值给变量clean_data
            # 将字典里面的confirm_password键值对删除
            clean_data.pop('confirm_password')
            # 用户头像
            file_obj = request.FILES.get('avatar')
            """针对用户头像一定要判断是否传值，不能直接添加到字段里去"""
            if file_obj:
                clean_data['avatar'] = file_obj
            # 直接操作数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)

    return render(request, 'register.html', locals())


# 登录功能
def login(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 1. 验证验证码是否正确   忽略大小写(通过转成大写或者小写进行比较)
        if request.session.get('code').upper() == code.upper():
            # 2. 校验用户名和密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或者密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


from PIL import Image, ImageDraw, ImageFont

"""
 Image：生成图片
 ImageDraw：能够在图片上乱涂乱画
 ImageFont：控制字体样式
"""
import random
from io import BytesIO, StringIO

"""
内存管理模块
BytesIO,:临时帮你存储数据，返回的时候数据是二进制格式
StringIO：临时帮你存储数据，返回的时候数据是字符串格式
"""


# 随机数
def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


# 图片验证码
def get_code(request):
    img_obj = Image.new(mode='RGB', size=(430, 35), color=get_random())
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/22.ttf', 30)  # 字体样式和大小

    # 随机验证码 五位数的随机验证码（数字，小写字母，大写字母）
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))  # chr 把数字转成对应的ascii对应的字符
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 从上面三个里随机选一个
        tmp = random.choice([random_lower, random_int, random_upper])
        # 将产生的随机字符串写入到图片上
        """为什么一个个写而不是生成好了之后再写
        因为一个个写能控制每个字体之间的间隙，而生成好的没法控制间隙
        """
        img_draw.text((i * 50 + 90, -1), tmp, get_random(), img_font)
        # 拼接随机i字符串
        code += tmp
    print(code)
    # 随机验证码在登录的视图函数里要用到，要比对，所以要存起来，其他视图函数也能拿到
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


# 首页
def home(request):
    # 查询本网站所有的文章数据展示到前端页面
    article_queryset = models.Article.objects.all()

    return render(request, 'home.html', locals())


# 修改密码
@login_required
def set_password(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            if is_right:
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg'] = '修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
        return JsonResponse(back_dic)


# 退出登录
@login_required
def logout(request):
    auth.logout(request)
    return redirect('home')


# 个人站点页面搭建
def site(request, username, **kwargs):
    """

    :param request:
    :param username:
    :param kwargs:如果该参数有值，也就意味着需要对article_list做额外的筛选工作
    :return:
    """
    # 校验当前用户名是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 用户不存在返回404页面
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    # 查询当前个人站点下的所有文章
    article_list = models.Article.objects.filter(blog=blog)  # 侧边栏的筛选其实就是对article_list再进一步筛选
    if kwargs:

        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 判断用户到底想按照哪个条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    # # 1.查询当前用户所有的分类及分类下的文章个数
    # category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
    #     'name',
    #     'count_num', 'pk')
    # # 2.查询当前所有用户的标签及标签下的标签数
    # tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
    #     'name',
    #     'count_num', 'pk')
    # # 3.按照年月统计所有的文章
    # date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
    #     'month').annotate(count_number=Count('pk')).values_list('month', 'count_number')
    return render(request, 'site.html', locals())


# 文章详情
def article_detail(request, username, article_id):
    user_obj=models.UserInfo.objects.filter(username=username).first()
    blog=user_obj.blog
    # 先获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id,blog__userinfo__username=username).first()
    if not article_obj:
        return render(request,'error.html')
    # 获取当前文章所有的内容
    comment_list = models.Comment.objects.filter(article=article_obj)
    return  render(request,'article_detail.html',locals())
