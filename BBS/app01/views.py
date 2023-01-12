# views.py
import json
import os.path

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from app01.myforms import MyRegForm
from app01 import models
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
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
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 先获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    if not article_obj:
        return render(request, 'error.html')
    # 获取当前文章所有的内容
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())


# 点赞点踩
def up_or_down(request):
    """
    1.校验用户是否登录
    2.判断当前文章是否是当前用户的，自己不能给自己点赞点踩
    3.当前用户是否已经给当前文章点过了，点过了就不能再点了
    4.操作数据库
    :param request:
    :return:
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        # 1.先判断当前用户是否登录
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            is_up = json.loads(is_up)
            # 2.判断当前文章是否是当前用户自己写的  根据文章id查询文章对象，根据文章对象查作者，跟request.user比对
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                # 3.校验当前用户是否已经点赞过了
                is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    # 4.操作数据库   同步操作普通字段
                    # 判断当前用户点了赞还是点了踩，从而决定给哪个字段+1
                    if is_up:
                        # 给点赞数加1
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功!!'
                    else:
                        # 给点踩数+1
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        back_dic['msg'] = '点踩成功!!'
                    # 操作点赞点踩表
                    models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '你已经点过了，不能再点了！'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '自己不能给自己点'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '请先<a href="/login/">登录</a>'

        return JsonResponse(back_dic)


from django.db import transaction


# 评论
def comment(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            if request.user.is_authenticated:
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                # 直接操作评论表存储数据 两张表
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                                  parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '用户未登录'

            return JsonResponse(back_dic)


# 后台管理
from utils.mypage import Pagination


@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog)
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count(), per_page_num=5)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup


# 添加文章
@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')

        soup = BeautifulSoup(content, 'html.parser')
        # 获取所有的标签
        tags = soup.find_all()
        for tag in tags:
            # print(tag.name)
            if tag.name == 'script':
                # 删除标签
                tag.decompose()
        # 文章简介
        # 1.先简单暴力的直接切取content  150个字符
        # desc = content[0:150]
        # 2.截取文本150个
        desc = soup.text[0:150]

        article_obj = models.Article.objects.create(
            title=title,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            blog=request.user.blog,
        )
        # 文章和标签的关系表是我们自己创建的，无法 使用add,set,remoce,clear方法
        # 自己去操作关系表  一次性可能需要创建多条数据， 批量插入数据 bulk_create()
        article_obj_list = []
        for i in tag_id_list:
            tag_article_obj = models.ArticleToTag(article=article_obj, tag_id=i)
            article_obj_list.append(tag_article_obj)
        # 批量插入数据
        models.ArticleToTag.objects.bulk_create(article_obj_list)
        # 跳转到后台管理文件展示页面
        return redirect('/backend/')

    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)

    return render(request, 'backend/add_article.html', locals())


# 编辑器上传图片
from BBS import settings


def upload_image(request):
    if request.method == 'POST':
        back_dic = {'erro': 0}
        # 获取用户上传的图片对象
        file_obj = request.FILES.get('imgFile')
        # 手动拼接存储文件路径
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        # 优化操作，先判断当前文件夹是否存在，不存在则创建
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        # 拼接图片完整路径
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url'] = '/media/article_img/%s' % file_obj.name
        return JsonResponse(back_dic)


# 修改头像
@login_required
def set_avatar(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)
        user_obj=request.user
        user_obj.avatar=file_obj
        user_obj.save()
        return redirect('/home/')
    blog = request.user.blog
    username = request.user.username

    return render(request, 'set_avatar.html', locals())
