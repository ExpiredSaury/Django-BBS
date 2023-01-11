# BBS项目开发

bbs是一个前后端不分离的全栈项目，前后端需要自己一步步完成

### 1、流程

```python
# 1. 需求分析
	架构师+产品经理+开发组组长
    在跟客户谈需求之前，会大致了解客户的需求，然后自己先设计出一套比较好写的方案，在个客户沟通交流中，引导客户往我们想好的方案上靠。
    形成一个初步方案，
# 2. 项目设计
	架构师干的活
    编程语言的选择
    框架选择
    数据库选择  主库:MySQL，缓存数据库:redis,mongondb
	功能划分
    	将整个项目划分成几个功能模块
    找组长开会，
        	给每个组分发任务
    项目报价
    	技术这块需要多少人力，多少天（一个程序员一天按照1500~2000大致）
        产品经理公司层面：再加点钱，（人力，物力）
        公司财务
        公司老板签字确认
    产品经理去跟客户沟通
    后续需要加功能，继续加钱
    
    
# 3.分组开发
	组长找组员开会，安排各自的功能模块，
    我们其实就是再架构师设计好的框架里填写代码而已(码畜)
    
    我们在写代码的时候，写完需要自己先测试是否有bug
    如果有一个些显而易见的bug，你没有避免而是直接交给测试部门测试出来，那么就可能需要扣绩效了（一定要跟测试搞好关系）
    薪资组成 15k (合理合规合法的避税)
    	底薪	10k
        绩效	3k
        岗位津贴 1k
        生活补贴 1k
# 4. 测试
	测试部门测试代码
    压力测试
    .....
# 5. 交付上线
	1.交给对放的运维人员
    2.直接上线到我们的服务器上，收取维护费
    3.其他.....
```

### 2、==表设计==

```python
"""
一个项目最终的不是业务逻辑的书写
而是前期的表设计，只要将表设计好了，后续的功能书写才能一帆风顺

表设计
	1.用户表
		继承AbstractUser
		额外扩展字段
			phone 电话
			avatar	用户头像
			create_time	创建时间
		外键字段
		一对一个人站点表 
        
        
	2.个人站点表
		site_name 个人站点名称
		site_title  站点标题
		site_theme  站点样式 css，js
		
	3.文章标签表
		name 标签名
		
		外键字段 
		一对多个人站点表
		
	4.文章分类表
		name 分类名
		
		外键字段 
		一对多个人站点表
		
	5.文章表
		title 文章标题 
		desc 文章简介
		content 文章内容
		create_time 发布时间
		
		数据库字段设计优化（虽然下述参数字段，可以通过Orm从其他表计算得出，但是效率太低，）
		up_num 点赞数
		down_num 点踩数
		comment_num 评论数
		
		外键字段
		一对多个人站点
		多对多文章标签表
		一对多文章分类
		
		
	6.点赞点踩表
		用来记录哪个用户给那篇文章点了赞还是点了踩
		user    ForenginKey(to='User')
		artice	ForenginKey(to='Article')
		is_up   BooleanField()
		
		1	1	1
		1	2	1	
		1	3	0	
		2	1	1
		
		
		
	7.文章评论表
		用来记录哪个用户给那篇文章写了哪些评论内容
		user 				ForenginKey(to='User')
		artice				ForenginKey(to='Article')
		content				CharFeild()
		comment_time		DateField()	
		#自关联
		parent				ForenginKey(to='Comment' null=True)
		#orm提供的自关联写法
		parent				ForenginKey(to='self',null=True)
		
		
		id		user_id		article_id		parent_id
		1			1			1						
		2			2			1				1
		
根评论子评论的概念
	根评论直接评论当前发布的内容的
	子评论是评论别人的评论
	
	一个根评论可以有多个子评论
	一个多个子评论只属于一个根评论
	
	根评论与子评论是一对多的关系
	
"""
```



![image-20221113112818038](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/20221212121805.png)

### 3、表创建及同步

```python
"""数据库选择Mysql，由于django自带的sqllite3对日期不敏感，所以换成Mysql"""
```

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bbs',
        'USER':'root',
        'PASSWORD':'123457',
        'HOSR':'127.0.0.1',
        'PORT':3306,
        'CHARSET':'utf8'
    }
}

#在随便哪个__init__.py中写入如下代码
import pymysql
pymysql.install_as_MySQLdb()
```

```python
# models.py
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(null=True, verbose_name='手机号')
    # 头像
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.jpg', verbose_name='用户头像')
    """给avatar字段传文件对象，该文件会自动存储到avatar文件下，然后avatar字段只保存文件路径avatar/default.jpg"""
    create_time = models.DateField(auto_now_add=True)

    """外键字段"""
    blog = models.OneToOneField(to='Blog', null=True, on_delete=models.CASCADE)


class Blog(models.Model):
    site_name = models.CharField(max_length=32, verbose_name='站点名称')
    site_title = models.CharField(max_length=32, verbose_name='站点标题')
    site_theme = models.CharField(max_length=64, verbose_name='站点样式')  # 存css/js文件路径


# 文章分类
class Category(models.Model):
    name = models.CharField(max_length=32, verbose_name='文章分类')
    """外键字段"""
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='文章标签')
    """外键字段"""
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)


class Article(models.Model):
    title = models.CharField(max_length=64, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章简介')
    # 文章内容很多，一般都使用TextField
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=True)
    # 数据库字段设计优化
    up_num = models.BigIntegerField(default=0, verbose_name='文章点赞数')
    down_num = models.BigIntegerField(default=0, verbose_name='文章点踩数')
    comment_num = models.BigIntegerField(default=0, verbose_name='文章评论数')
    """外键字段"""
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', null=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(to='Tag',
                                  through='ArticleToTag',
                                  through_fields=('article', 'tag'))


# 文章表和标签表的第三张关系表
class ArticleToTag(models.Model):
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    tag = models.ForeignKey(to='Tag', on_delete=models.CASCADE)


class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    is_up = models.BooleanField()  # 布尔值，存0/1


class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    content = models.CharField(max_length=255, verbose_name='评论内容')
    comment_time = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    # 自关联
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True)  # 有些评论就是根评论
```

项目根目录创建avatar文件，**注意：**这只是前期需要，后期会使用别的

![image-20230107091223252](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/image-20230107091223252.png)

settings.py中配置

```python
#继承了AbstractUser就得在配置文件中设置此代码
AUTH_USER_MODEL = 'app01.UserInfo'
```

执行数据迁移命令

```python
python manage.py makemigrations
python manage.py migrate
```





### 4、注册功能

，用户头像前端实时展示

ajax

```python
"""之前是在views.py中写froms组件代码

为了解耦合，应该将所有forms组件代码单独写一个地方

如果项目至始至终只用到一个forms组件，那么直接建一个py文件即可
但是如果你的项目需要使用多个forms组件，那么你可以创建一个文件夹，在文件夹内根据forms组件的功能的不同创建多个py文件
myforms文件夹
	regform.py
	loginform.py
	userform.py
	orderform.py

1.利用forms组件渲染前端标签
	1.不利用form表单提交而是用ajax提交
	2.但是需要用到form标签来包含我们所有的获取用户数据的html代码
		$('#myform').serializeArray()
		获取到fomr标签内所有普通键值对的数据
		[{},{},{}]

2.手动渲染获取用户头像标签
      <label for="myfile">头像
                        <img src="{% static 'imgs/default.png' %}" id="myimg" alt="" width='80'
                             style="margin-top: 20px;margin-left: 10px">
                    </label>
                    <input type="file" id="myfile" name="avatar" style="display: none">
                    只要在label里面的内容点击 就会跳转到for指定的标签上
3.如何实时展示 用户头像
	1.利用文件阅读器
	2.change事件
	3.onload等待加载完毕
5.一旦用户信息不合法，如何精确的渲染提示信息
    1.forms组件渲染的标签组件都有一个固定的特点
        id_字段名
        ps:如何获取id值 form.auto_id
              <label for="{{ form.auto_id }}">{{ form.label }}</label>
	2.根据后端返回的字段以及字段对应的报错信息
    	自己手动拼接对应字段的id值
    3.提示功能完善
    	1.jQuery链式操作
    	2.input获取焦点事件
"""
```

#### **forms组件**

```python
# 书写针对用户表的forms组件|代码
# app01文件夹下的myforms.py
from django import forms
from app01 import models


class MyRegForm(forms.Form):
    username = forms.CharField(label='用户名',
                               max_length=8,
                               min_length=3,
                               error_messages={
                                   'min_length': '用户名最小3位',
                                   'max_length': '用户名最大8位',
                                   'required': '用户不能为空',
                               },
                               #还需要标签具有bootstrap样式
                               widget=forms.widgets.TextInput(attrs={'class': 'form-control'})                               )
    password = forms.CharField(label='密码',
                               max_length=8,
                               min_length=3,
                               error_messages={
                                   'min_length': '密码最小3位',
                                   'max_length': '密码最大8位',
                                   'required': '密码不能为空',
                               },
                               widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'})                               )
    confirm_password = forms.CharField(label='确认密码',
                                       max_length=8,
                                       min_length=3,
                                       error_messages={
                                           'min_length': '确认密码最小3位',
                                           'max_length': '确认密码最大8位',
                                           'required': '确认密码不能为空',
                                       },
                                       widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'})
                                       )
    email = forms.EmailField(label='邮箱',
                             error_messages={
                                 'required': '用户不能为空',
                                 'invalid': '邮箱格式不正确',
                             },
                             widget=forms.widgets.EmailInput(attrs={'class': 'form-control'})
                             )

    # 钩子函数
    # 局部钩子：校验用户是否已经存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # 去数据库中校验
        is_exist = models.UserInfo.objects.filter(username=username)
        if is_exist:
            # 提示信息:
            self.add_error('username', '用户名已存在')
        return username

    # 全局钩子:校验两次密码是否一致
    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not password == confirm_password:
            self.add_error('confirm_password', '两次密码不一致')

        return self.cleaned_data

```

静态资源配置

```python
STATIC_URL = '/static/'
STATICFILES_DIRS=[
    BASE_DIR / 'static'
]
```

![image-20230107093759892](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/image-20230107093759892.png)

静态资源引入

```html
{% load static %}
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script src="{% static 'js/jQuery-3.6.0-min.js' %}"></script>
    <link href="{% static 'bootstrap-3.4.1-dist/css/bootstrap.min.css' %}" rel="stylesheet">
    <script src="{% static 'bootstrap-3.4.1-dist/js/bootstrap.min.js' %}"></script>
</head>
```



#### **前端**

```html
<!--register.html---->

<body>
<div class="container-fluid">
    <div class="row">
        <div class="col-md-8 col-md-offset-2">
            <h1 class="text-center">注册</h1>
            <form id="myform">  <!-----这里不用form表单提交数据，只是单纯的用已给form标签而已--->
                {% csrf_token %}
                {% for form in form_obj %}
                    <div class="form-group">
                        <label for="{{ form.auto_id }}">{{ form.label }}</label>
                        {{ form }}
                        <span style="color: red" class="pull-right">{{ form.errors.0 }}</span>
                    </div>
                {% endfor %}

                <div class="form-group">
                    <label for="myfile">头像
                        <img src="{% static 'imgs/default.png' %}" id="myimg" alt="" width='80'
                             style="margin-top: 20px;margin-left: 10px">
                    </label>
                    <input type="file" id="myfile" name="avatar" style="display: none">
                </div>

                <input type="button" class="btn btn-primary pull-right" value="注册" id="id_commit">

            </form>

        </div>

    </div>
</div>

<script>
    $('#myfile').change(function () {
        //文件阅读器对象
        //1.先生成一个文件对象
        let myFileReaderObj = new FileReader();
        //2. 获取用户上传的头像文件
        let fileObj = $(this)[0].files[0];
        //3. 将文件对象交给阅读器对象读取
        myFileReaderObj.readAsDataURL(fileObj)  //异步操作 IO操作
        //4.利用文件阅读器将文件展示到前端页面  修改src属性
        //等待文件阅读器加载完毕后再执行
        myFileReaderObj.onload = function () {
            $('#myimg').attr('src', myFileReaderObj.result)
        }

    })
    $('#id_commit').click(function () {
        //发送ajax，但是我们发送的数据中，既包含普通的简直，也包含文件
        let formDataObj = new FormData()
        //1.添加普通键值对
        {#console.log($('#myform').serializeArray()) #}
        $.each($('#myform').serializeArray(), function (index, obj) {
            formDataObj.append(obj.name, obj.value)
        })
        //2.添加文件对象
        formDataObj.append('avatar', $('#myfile')[0].files[0])
        //3.发送ajax请求
        $.ajax({
            url: '',
            type: 'post',
            data: formDataObj,
            //需要指定两个关键性参数
            contentType: false,
            processData: false,
            success: function (args) {
                if (args.code == 1000) {
                    //跳转登录页面
                    window.location.href = args.url
                } else {
                    //将对应的错误提示展示到对应的input框下面
                    $.each(args.msg, function (index, obj) {
                        let targetId = '#id_' + index;
                        $(targetId).next().text(obj[0]).parent().addClass('has-error')
                    })
                }
            }

        })
    })
    //给所有的input框绑定获取焦点事件
    $('input').focus(function (){
        //将input框下面的span标签和外面的div标签修改内容及属性
        $(this).next().text('').parent().removeClass('has-error')
    })
</script>

</body>
```

#### **后端**

```python
#urls.py
from app01 import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',views.register,name='register')
]
```



```python
#views.py
from django.http import JsonResponse
from django.shortcuts import render
from app01.myforms import MyRegForm
from app01 import models

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
```

### 5、登录功能

实现图片验证码

ajax

```python
"""
img标签的src属性
	1.图片路径
	2.url后缀（自动朝该url发送get请求获取数据）
	3.图片的二进制数据
		
我们的计算机上面之所以能输出各式各样的字体样式，内部其实对应的是一个个.ttf结尾的文件

1.借助于pillow模块
	Image ImageDraw ImageFont
2.需要借助于内存管理器io模块
	BytesIo StringIo
3.字体样式  .ttf文件
4.手动产生随机验证码  （搜狗笔试题）
	random模块
	chr内置方法
5.验证码校验
	
"""
```

#### **前端**

```html
{% load static %}
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <!---<script src="../jQuery-3.6.0-min.js"></script>--->
    <script src="https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    
    <link rel="stylesheet" href="{% static 'bootstrap-3.4.1-dist/css/bootstrap.min.css' %}">
    <script src="{% static 'bootstrap-3.4.1-dist/js/bootstrap.min.js' %}"></script>
</head>
<body>
<div class="container-fluid">
    <div class="row">
        <div class="col-md-offset-2 col-md-8">
            <h1 class="text-center">登录</h1>
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" name="username" id="username" class="form-control">
            </div>
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" name="password" class="form-control" id="password">
            </div>
            <div class="form-group">
                <label for="">验证码</label>
                <div class="row">
                    <div class="col-md-6">
                        <input type="text" name="code" id="id_code" class="form-control">
                    </div>
                    <div class="col-md-6">
                        <img src="{% url 'code' %}" alt="" width="450" height="35" id="id_img">
                    </div>
                </div>

            </div>
            <input type="button" class="btn btn-success" value="登录" id="id_commit">
            <span style="color: red" id="error"></span>
        </div>
    </div>
</div>

<script>
    $('#id_img').click(function () {
        //1.获取标签之前的src
        let oldVal = $(this).attr('src');
        $(this).attr('src', oldVal += '?')
    })
    //点击按钮，发送ajax请求
    $('#id_commit').on('click', function () {
        $.ajax({
            url: '',
            type: 'post',
            data: {
                'username': $('#username').val(),
                'password': $('#password').val(),
                'code': $('#id_code').val(),
                'csrfmiddlewaretoken':'{{ csrf_token }}',
            },
            success: function (args) {
                if (args.code == 1000) {
                    //跳转到首页
                    window.location.href = args.url
                } else {
                    //渲染错误信息
                    $('#error').text(args.msg)

                }
            }

        })
    })
</script>
</body>
</html>
```

#### **后端**

```python
#urls.py
path('login/', views.login, name='login'),
# 图片验证码相关
path('get_code/', views.get_code, name='code'),

#views.py
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


"""
图片相关模块
pip install pillow
"""
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


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    """推导数据一：直接获取后端现成的图片二进制数据发送给前端"""

    # with open(r'static/imgs/title.png', 'rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    """推导步骤2：利用pillow模块，动态产生图片"""
    # # img_obj = Image.new(mode='RGB', size=(430, 35), color='green')
    # # img_obj = Image.new(mode='RGB', size=(430, 35), color=(123, 23, 12))
    # img_obj = Image.new(mode='RGB', size=(430, 35), color=get_random())
    # # 先将图片对象保存起来
    # with open('xxx.png', 'wb') as f:
    #     img_obj.save(f, 'png')
    # # 再将图片对象读取出来
    # with open('xxx.png', 'rb') as f:
    #     data = f.read()
    # return HttpResponse(data)
    """推导步骤3:步骤2文件存储繁琐，IO效率低，借助于内存管理器模块"""
    # img_obj = Image.new(mode='RGB', size=(430, 35), color=get_random())
    # io_obj = BytesIO()  # 生成一个内存管理器对象，可以看成是一个文件句柄
    # img_obj.save(io_obj, 'png')
    # return HttpResponse(io_obj.getvalue())  # 从内存管理器中读取二进制数据返回给前端

    """最终步骤4：写图片验证码"""
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
```

### 6、搭建BBS首页

#### 导航条搭建

```html
<nav class="navbar navbar-inverse">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
        <span class="sr-only">BBS</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="#">BBS</a>
    </div>

    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <ul class="nav navbar-nav">
        <li class="active"><a href="#">博客 <span class="sr-only">(current)</span></a></li>
        <li><a href="#">文章</a></li>
        <li class="dropdown">
          <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">更多 <span class="caret"></span></a>
          <ul class="dropdown-menu">
            <li><a href="#">Action</a></li>
            <li><a href="#">Another action</a></li>
            <li><a href="#">Something else here</a></li>
            <li role="separator" class="divider"></li>
            <li><a href="#">Separated link</a></li>
            <li role="separator" class="divider"></li>
            <li><a href="#">One more separated link</a></li>
          </ul>
        </li>
      </ul>
      <form class="navbar-form navbar-left">
        <div class="form-group">
          <input type="text" class="form-control" placeholder="Search">
        </div>
        <button type="submit" class="btn btn-default">Submit</button>
      </form>
      <ul class="nav navbar-nav navbar-right">
        <li><a href="#">Link</a></li>
        <li class="dropdown">
          <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Dropdown <span class="caret"></span></a>
          <ul class="dropdown-menu">
            <li><a href="#">Action</a></li>
            <li><a href="#">Another action</a></li>
            <li><a href="#">Something else here</a></li>
            <li role="separator" class="divider"></li>
            <li><a href="#">Separated link</a></li>
          </ul>
        </li>
      </ul>
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>
```



**动态展示用户名称**

导航条根据用户是否登录展示不同的内容

>当用户登录之后显示用户名和更多操作，当用户没有登录显示注册和登录

![image-20230111142029706](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/image-20230111142029706.png)

```html
{% if request.user.is_authenticated %}
    <li><a href="#">{{ request.user.username }}</a></li>
    <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
           aria-expanded="false">更多 <span class="caret"></span></a>
        <ul class="dropdown-menu">
            <li><a href="#">修改密码</a></li>
            <li><a href="#">修改头像</a></li>
            <li><a href="#">后台管理</a></li>
            <li role="separator" class="divider"></li>
            <li><a href="#">退出登录</a></li>
        </ul>
    </li>
{% else %}
    <li><a href="{% url 'register' %}">注册</a></li>
    <li><a href="{% url 'login' %}">登录</a></li>
{% endif %}
```

##### **修改密码**

> 只有登录的用户才能修改密码

```html
<!--home.html-->
<li class="dropdown">
    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
       aria-expanded="false">更多 <span class="caret"></span></a>
    <ul class="dropdown-menu">
        <li><a href="#" data-toggle="modal"
               data-target=".bs-example-modal-lg">修改密码</a></li>
        <li><a href="#">修改头像</a></li>
        <li><a href="#">后台管理</a></li>
        <li role="separator" class="divider"></li>
        <li><a href="#">退出登录</a></li>
    </ul>
    <!-- 弹出框 -->
    <div class="modal fade bs-example-modal-lg" tabindex="-1" role="dialog"
         aria-labelledby="myLargeModalLabel">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
                <h1 class="text-center">修改密码</h1>
                <div class="row">
                    <div class="col-md-8 col-md-offset-2">
                        <div class="form-group">
                            <label for="">用户名</label>
                            <input type="text" class="form-control" disabled
                                   value="{{ request.user.username }}">
                        </div>
                        <div class="form-group">
                            <label for="">原密码</label>
                            <input type="text" class="form-control" id="id_old_password">
                        </div>
                        <div class="form-group">
                            <label for="">新密码</label>
                            <input type="text" class="form-control" id="id_new_password">
                        </div>
                        <div class="form-group">
                            <label for="">确认密码</label>
                            <input type="text" class="form-control" id="id_confirm_password">
                        </div>
                        <button type="button" class="btn btn-default" data-dismiss="modal">取消</button>
                        <button class="btn btn-primary" id="id_edit">修改</button>
                        <span style="color: red" id="id_error"></span>
                        <br>
                        <br>

                    </div>
                </div>
            </div>
        </div>
    </div>
</li>



<script>
    $('#id_edit').click(function () {
        $.ajax({
            url: '/set_password/',
            type: 'post',
            data: {
                'old_password': $('#id_old_password').val(),
                'new_password': $('#id_new_password').val(),
                'confirm_password': $('#id_confirm_password').val(),
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function (args) {
                if (args.code == 1000) {
                    {#刷新页面#}
                    window.location.reload()
                }else{
                    $('#id_error').text(args.msg)

                }
            }
        })
    })
</script>
```

全局配置装饰器

```python
#settings.py
LOGIN_URL = '/login/'
```



```python
#urls.py
# 修改密码
path('set_password/', views.set_password, name='set_password'),

#views.py
from django.contrib.auth.decorators import login_required

@login_required
def set_pwd(request):
    back_dic = {'code': 1000, 'msg': ''}
    if request.is_ajax():
        if request.method == 'POST':
            old_pwd = request.POST.get('old_pwd')
            new_pwd = request.POST.get('new_pwd')
            confirm_pwd = request.POST.get('confirm_pwd')
            is_right = request.user.check_password(old_pwd)
            if is_right:
                if new_pwd == confirm_pwd:
                    request.user.set_password(new_pwd)
                    request.user.save()
                    back_dic['msg'] = '修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
        return JsonResponse(back_dic)
```

##### **退出登录**

```python
# home.html
<li><a href="{% url 'logout' %}">退出登录</a></li>


# urls.py
path('logout/',views.logout,name='logout')
# views.py

from django.shortcuts import redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required

@login_required
def logout(request):
    auth.logout(request)
    return redirect('home')
```

#### 首页搭建

##### 首页282布局

```html
<div class="container-fluid">
    <div class="row">
        <div class="col-md-2">
            {#面板#}
            <div class="panel panel-primary">
                <div class="panel-heading">
                    <h3 class="panel-title">重金求子</h3>
                </div>
                <div class="panel-body">
                    事成之后，上海别墅一套，外加现金500w
                </div>
            </div>
            <div class="panel panel-danger">
                <div class="panel-heading">
                    <h3 class="panel-title">千万大奖</h3>
                </div>
                <div class="panel-body">
                    抓紧联系：12345761313
                </div>
            </div>
            <div class="panel panel-info">
                <div class="panel-heading">
                    <h3 class="panel-title">线上赌场</h3>
                </div>
                <div class="panel-body">
                    性感荷官在线发牌，还在等什么？？？
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            
			<!--文章数据展示区域-->
            <!--文章数据展示区域-->
            <!--文章数据展示区域-->
            
        </div>
        
        <div class="col-md-2">
            {#面板#}
            <div class="panel panel-primary">
                <div class="panel-heading">
                    <h3 class="panel-title">重金求子</h3>
                </div>
                <div class="panel-body">
                    事成之后，上海别墅一套，外加现金500w
                </div>
            </div>
            <div class="panel panel-danger">
                <div class="panel-heading">
                    <h3 class="panel-title">千万大奖</h3>
                </div>
                <div class="panel-body">
                    抓紧联系：12345761313
                </div>
            </div>
            <div class="panel panel-info">
                <div class="panel-heading">
                    <h3 class="panel-title">线上赌场</h3>
                </div>
                <div class="panel-body">
                    性感荷官在线发牌，还在等什么？？？
                </div>
            </div>
        </div>
    </div>
</div>
```

##### **admin后台管理添加数据**

```python
"""django提供了一个可视化的界面，方便对模型表进行增删改查操作
"""
```

先创建超级用户，然后登录，登陆后发现没有其他表，**如下图**：

![image-20230111153930811](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/image-20230111153930811.png)

```python
"""
如果想要使用admin后台管理，需要先注册模型表
告诉admin需要操作哪些表
去应用下的admin.py种注册你的模型表
"""
#注册模型表
from django.contrib import admin
from App import models

# Register your models here.
admin.site.register(models.UserInfo)
admin.site.register(models.Blog)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Article)
admin.site.register(models.ArticleToTag)
admin.site.register(models.UpAndDown)
admin.site.register(models.Comment)
```

```python
#admin会给每一个注册了的模型表自动生成增删改查四条url
拿用户表为例:
http://127.0.0.1:8000/admin/app01/userinfo/   查
http://127.0.0.1:8000/admin/app01/userinfo/add/     增
http://127.0.0.1:8000/admin/app01/userinfo/1/change/    改
http://127.0.0.1:8000/admin/app01/userinfo/1/delete/    删

个人站点表为例
http://127.0.0.1:8000/admin/app01/blog/   查
http://127.0.0.1:8000/admin/app01/blog/add/     增
http://127.0.0.1:8000/admin/app01/blog/1/change/    改
http://127.0.0.1:8000/admin/app01/blog/1/delete/    删

"""
关键点就在于urls.py中自带的第一条url
	path('admin/', admin.site.urls),

前期需要自己手动录入数据
"""

#1.数据绑定尤其要注意用户和个人站点不要忘记绑定

#2.标签

#3.标签和文章
	千万不要把别人的文章绑定标签
```



![image-20221120210742677](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/20221210162428.png)

要想展示中文，可以在models.py中给每个表加上

```python
class Meta:
    verbose_name_plural = '自定义名称'  # 用来修改admin后台管理默认的表名
```

![image-20221120211249472](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/20221212121805-1.png)



![image-20221120211305579](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/20221212121805-2.png)

添加站点的时候发现不好识别，如下图：可以在models.py中加`__str__`方法

![image-20230111155803912](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/image-20230111155803912.png)

```python
# models.py
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(null=True, verbose_name='手机号')
    # 头像
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.jpg', verbose_name='用户头像')
    """给avatar字段传文件对象，该文件会自动存储到avatar文件下，然后avatar字段只保存文件路径avatar/default.jpg"""
    create_time = models.DateField(auto_now_add=True)

    """外键字段"""
    blog = models.OneToOneField(to='Blog', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '用户表'  # 用来修改admin后台管理默认的表名

    def __str__(self):
        return self.username
    
class Blog(models.Model):
    site_name = models.CharField(max_length=32, verbose_name='站点名称')
    site_title = models.CharField(max_length=32, verbose_name='站点标题')
    site_theme = models.CharField(max_length=64, verbose_name='站点样式')  # 存css/js文件路径

    class Meta:
        verbose_name_plural = '个人站点表'

    def __str__(self):
        return self.site_name
# 文章分类
class Category(models.Model):
    name = models.CharField(max_length=32, verbose_name='文章分类')
    """外键字段"""
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '文章分类'

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='文章标签')
    """外键字段"""
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '文章标签'

    def __str__(self):
        return self.name
    
class Article(models.Model):
    title = models.CharField(max_length=64, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章简介')
    # 文章内容很多，一般都使用TextField
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=True)
    # 数据库字段设计优化
    up_num = models.BigIntegerField(default=0, verbose_name='文章点赞数')
    down_num = models.BigIntegerField(default=0, verbose_name='文章点踩数')
    comment_num = models.BigIntegerField(default=0, verbose_name='文章评论数')
    """外键字段"""
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', null=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(to='Tag',
                                  through='ArticleToTag',
                                  through_fields=('article', 'tag'))

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = '文章表'


# 文章表和标签表的第三张关系表
class ArticleToTag(models.Model):
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    tag = models.ForeignKey(to='Tag', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '文章和标签的第三张关系表'


class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    is_up = models.BooleanField()  # 布尔值，存0/1

    class Meta:
        verbose_name_plural = '点赞点踩'


class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    content = models.CharField(max_length=255, verbose_name='评论内容')
    comment_time = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    # 自关联
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True)  # 有些评论就是根评论

    class Meta:
        verbose_name_plural = '评论'

```

在用admin后台管理添加用户信息点击save的时候，会出现报错信息

![image-20230111161003462](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/image-20230111161003462.png)

，

> 注意：null=True是告诉数据库可以为空，但是admin后台管理不允许为空，如果想要它为空，需要再加上blank=True

```python
class UserInfo(AbstractUser):
    phone = models.BigIntegerField(null=True, verbose_name='手机号',blank=True)
```



**扩展：admin路由分发的本质**

```python
# 路由分发的本质 include   可以无限制的嵌套n多层 path('index/',([],None,None))
 #列表里可以无限制的嵌套   
    path('index/', ([
        path('index_1/', ([
            path('index_1_1/', index),
            path('index_1_2/', index)
        ], None, None)),
        path('index_2/', index)
    ], None, None)),

#views,py
from django.shortcuts import HttpResponse

def index(request):
    return HttpResponse('index')    
    
```

![image-20221121144353582](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/20221212121805-3.png)

##### 首页数据展示

```python
<div class="col-md-8">
            <!--文章数据展示区域-->
            <ul class="media-list">
                {% for article_obj in article_queryset %}
                    <li class="media">
                        <h4 class="media-heading"><a href="">{{ article_obj.title }}</a></h4>
                        <div class="media-left">
                            <a href="#">
                                <img class="media-object" src="{% static 'imgs/default.png' %}" alt="..." width='50px'>
                            </a>
                        </div>
                        <div class="media-body">
                            {{ article_obj.desc }}
                        </div>
                        <br>
                    <div>
                        <span><a href="#">{{ article_obj.blog.userinfo.username }}&nbsp;&nbsp;</a></span>
                        <span>发布于&nbsp;&nbsp;</span>
                        <span>{{ article_obj.create_time|date:'Y-m-d' }}&nbsp;&nbsp;</span>
                        <span><span class="glyphicon glyphicon-comment"></span>评论({{ article_obj.comment_num }})&nbsp;&nbsp;</span>
                        <span><span class="glyphicon glyphicon-thumbs-up"></span>点赞({{ article_obj.up_num }})</span>
                    </div>
                    </li>
                    <hr>
                {% endfor %}

            </ul>
 </div>
```

```python
# 首页
#urls.py
path('home/', views.home, name='home'),
#views.py
def home(request):
    # 查询本网站所有的文章数据展示的前端页面，这里可以使用分页器做分页，
    aritcle_queryset = models.Article.objects.all()
    return render(request, 'home.html', locals())
```

##### **media配置及用户头像展示**

```python
"""
1.网址所使用的静态文件默认放在static文件夹下
2.用户上传的静态文件也应该单独放在某个文件夹下	
"""
```

**media配置**：该设置可以让用户上传的所有文件都固定存放在某一个指定的文件夹下

```python
网站所使用 的静态资源默认都放在static文件夹下

#settings.py中
# 配置用户上传的文件存储位置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')#文件名随意
会自动创建多级目录
```

![image-20221121092212547](https://gitee.com/zh_sng/cartographic-bed/raw/master/img/20221212121759.png)

**如何开设后端指定文件夹资源**

```python
# 暴露后端指定文件夹资源
# 在暴露资源的时候，一定要明确该资源是否可以暴露
from django.views.static import serve
from BBS import settings  #项目下的settings.py文件
#固定代码
re_path(r'media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT})
```

**头像展示**

```html
<img class="media-object" src="/media/{{article_obj.blog.userinfo.avatar }}" alt="..." width='50px'>
```

##### **图片防盗链**

```python
#如何避免别的网站直接通过本网站的url访问本网站的资源
#简单的防盗链
 可以做到请求来的时候先看看当前请求是从哪个网站过来的
 如果是本网站那么正常访问
如果是其他网站直接拒绝
	请求头里有一个专门记录请求来自于哪个网址的参数
    	Referer
#如何避免
	1.直接修改请求头referer
    2.直接写爬虫把对方网站的所有资源下载到我们自己的服务器上
```



### 7、个人站点页面搭建

#### 404页面

> 根据用户名进入个人站点，用户名不存在则返回404页面

```python
# 个人站点页面搭建
#urls.py
re_path(r'^(?P<username>\w+)/$',views.site,name='site')

#views.py

def site(request,username):
    # 校验当前用户名是否存在
    user_obj=models.UserInfo.objects.filter(username=username).first()
    #用户不存在返回404页面
    if not user_obj:
        return  render(request,'error.html')

```

```html
<!--error.html--->
<html>
<head>
    <meta charset='utf-8'>

    <title>404 页面不存在 - 博客园</title>
    <style type='text/css'>
        body {
            margin: 8% auto 0;
            max-width: 400px;
            min-height: 200px;
            padding: 10px;
            font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
            font-size: 14px;
            padding-right: 200px;
            position: relative;
        }

        p {
            color: #555;
            margin: 15px 0px;
        }

        img {
            border: 0px;
        }

        .d {
            color: #404040;
        }

    </style>
</head>
<body>
<a href="/home/"> <img src='//common.cnblogs.com/images/logo_small.gif' alt=""></a>
<p><b>404.</b>抱歉，您访问的资源不存在</p>
<p class="d">请确认您输入的网址是否争取，如果问题持续存在，请发邮件 contact&#64;python666.com 与我们联系。</p>
<p><a href="/home/">返回网站首页</a></p>
</body>
</html>
```

在home.html中配置跳转的url

```html
 <span><a href="/{{ article_obj.blog.userinfo.username  }}/">{{ article_obj.blog.userinfo.username }}&nbsp;&nbsp;</a></span>
```



#### 导航条搭建

```html
<!--site.html--->
<nav class="navbar navbar-inverse">
    <div class="container-fluid">
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse"
                    data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                <span class="sr-only">BBS</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="#">{{ blog.site_title }}</a>
        </div>

        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
            <ul class="nav navbar-nav">
                <li class="active"><a href="#">博客 <span class="sr-only">(current)</span></a></li>
                <li><a href="#">文章</a></li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
                       aria-expanded="false">更多 <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="#">Action</a></li>
                        <li><a href="#">Another action</a></li>
                        <li><a href="#">Something else here</a></li>
                        <li role="separator" class="divider"></li>
                        <li><a href="#">Separated link</a></li>
                        <li role="separator" class="divider"></li>
                        <li><a href="#">One more separated link</a></li>
                    </ul>
                </li>
            </ul>
            <form class="navbar-form navbar-left">
                <div class="form-group">
                    <input type="text" class="form-control" placeholder="Search">
                </div>
                <button type="submit" class="btn btn-default">Submit</button>
            </form>
            <ul class="nav navbar-nav navbar-right">
                {% if request.user.is_authenticated %}
                    <li><a href="#">{{ request.user.username }}</a></li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
                           aria-expanded="false">更多 <span class="caret"></span></a>
                        <ul class="dropdown-menu">
                            <li><a href="#" data-toggle="modal"
                                   data-target=".bs-example-modal-lg">修改密码</a></li>
                            <li><a href="#">修改头像</a></li>
                            <li><a href="#">后台管理</a></li>
                            <li role="separator" class="divider"></li>
                            <li><a href="{% url 'logout' %}">退出登录</a></li>
                        </ul>
                        <!-- 弹出框 -->
                        <div class="modal fade bs-example-modal-lg" tabindex="-1" role="dialog"
                             aria-labelledby="myLargeModalLabel">
                            <div class="modal-dialog modal-lg" role="document">
                                <div class="modal-content">
                                    <h1 class="text-center">修改密码</h1>
                                    <div class="row">
                                        <div class="col-md-8 col-md-offset-2">
                                            <div class="form-group">
                                                <label for="">用户名</label>
                                                <input type="text" class="form-control" disabled
                                                       value="{{ request.user.username }}">
                                            </div>
                                            <div class="form-group">
                                                <label for="">原密码</label>
                                                <input type="text" class="form-control" id="id_old_password">
                                            </div>
                                            <div class="form-group">
                                                <label for="">新密码</label>
                                                <input type="text" class="form-control" id="id_new_password">
                                            </div>
                                            <div class="form-group">
                                                <label for="">确认密码</label>
                                                <input type="text" class="form-control" id="id_confirm_password">
                                            </div>
                                            <button type="button" class="btn btn-default" data-dismiss="modal">取消
                                            </button>
                                            <button class="btn btn-primary" id="id_edit">修改</button>
                                            <span style="color: red" id="id_error"></span>
                                            <br>
                                            <br>

                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </li>
                {% else %}
                    <li><a href="{% url 'register' %}">注册</a></li>
                    <li><a href="{% url 'login' %}">登录</a></li>
                {% endif %}


            </ul>
        </div><!-- /.navbar-collapse -->
    </div><!-- /.container-fluid -->
</nav>
```

#### 个人站点39布局

##### 文章展示区域

```html
<!--site.html--->
<div class="container-fluid">
    <div class="row">
        <div class="col-md-3">
           
                {# 侧边栏区域#}
            
        </div>
        <div class="col-md-9">
                  <!--文章数据展示区域-->
            <ul class="media-list">
                {% for article_obj in article_list %}
                    <li class="media">
                        <h4 class="media-heading"><a href="">{{ article_obj.title }}</a></h4>
                        <div class="media-left">
                            <a href="#">
                                <img class="media-object" src="/media/{{ article_obj.blog.userinfo.avatar }}" alt="..." width='50px'>
                            </a>
                        </div>
                        <div class="media-body">
                            {{ article_obj.desc }}
                        </div>

                    <div class="pull-right">
                        <span>posted&nbsp;&nbsp;</span>
                        <span>@&nbsp;&nbsp;</span>
                        <span>{{ article_obj.create_time|date:'Y-m-d' }}&nbsp;&nbsp;</span>
                        <span>{{ article_obj.blog.userinfo.username }}&nbsp;&nbsp;</span>
                        <span><span class="glyphicon glyphicon-comment"></span>评论({{ article_obj.comment_num }})&nbsp;&nbsp;</span>
                        <span><span class="glyphicon glyphicon-thumbs-up"></span>点赞({{ article_obj.up_num }})</span>
                        <span><a href="#">编辑</a></span>
                    </div>
                    </li>
                    <hr>
                {% endfor %}

            </ul>
        </div>
    </div>
</div>
```



```python
# 个人站点页面搭建
def site(request, username):
    # 校验当前用户名是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 用户不存在返回404页面
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    # 查询当前个人站点下的所有文章
    article_list=models.Article.objects.filter(blog=blog)
    return render(request,'site.html',locals())
```

##### 侧边栏展示区域

```python
#诠释每个用户都可以有自己的站点样式
 <link rel="stylesheet" href="/media/css/{{ blog.site_theme }}">
  内部给每个人开设自定义的css样式和js文件接口，并且用户自定义后会将用户的文件保存下来，之后再打开用户界面的时候会自动加载用户自己写的css和js文件从而实现每个用户界面不一样的情况
"""
django官网提供的一个orm语法

date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_number=Count('pk')).values_list('month', 'count_number')
"""

#如果出现日期报错的情况，去settings.py中修改以下代码
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False

```

```html
   <div class="col-md-3">

            {# 侧边栏区域#}
            <div class="panel panel-primary">
                <div class="panel-heading">
                    <h3 class="panel-title">文章分类</h3>
                </div>
                <div class="panel-body">
                    {% for category in category_list %}
                    <p><a href="">{{ category.0 }}({{ category.1 }})</a></p>
                    {% endfor %}
                </div>
            </div>
            <div class="panel panel-danger">
                <div class="panel-heading">
                    <h3 class="panel-title">文章标签</h3>
                </div>
                <div class="panel-body">
                    {% for tag in tag_list %}
                    <p><a href="">{{ tag.0 }}({{ tag.1 }})</a></p>
                    {% endfor %}
                </div>
            </div>
            <div class="panel panel-info">
                <div class="panel-heading">
                    <h3 class="panel-title">日期归档</h3>
                </div>
                <div class="panel-body">
    {% for date in date_list %}
    <p><a href="">{{ date.0|date:'Y年m月' }}({{ date.1 }})</a></p>
    {% endfor %}

                </div>
            </div>

        </div>
```

```python
# 个人站点页面搭建
def site(request, username):
    # 校验当前用户名是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 用户不存在返回404页面
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    # 查询当前个人站点下的所有文章
    article_list = models.Article.objects.filter(blog=blog)

    # 1.查询当前用户所有的分类及分类下的文章个数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name',
        'count_num')
    # 2.查询当前所有用户的标签及标签下的标签数
    tag_list=models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name',
        'count_num')
    # 3.按照年月统计所有的文章
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_number=Count('pk')).values_list('month', 'count_number')
    return render(request, 'site.html', locals())

```



##### **侧边栏筛选功能**

```python
侧边栏筛选功能
	1.多个url公用一个视图函数
    2.当多个url公用一个视图函数的时候，应该思考能否优化
    #re_path(r'^(?P<username>\w+)/category/(\d+)/', views.site),
    # re_path(r'^(?P<username>\w+)/tag/(\d+)/', views.site),
    # re_path(r'^(?P<username>\w+)/archive/(\w+)/', views.site),
    #  侧边栏筛选功能 上面的三条url合并成一条
    re_path(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site)
```



```html
<div class="container-fluid">
    <div class="row">
        <div class="col-md-3">
            <div class="panel panel-primary">
                <div class="panel-heading">
                    <h3 class="panel-title">文章分类</h3>
                </div>
                <div class="panel-body">
                    {% for category in category_list %}
                        <p><a href="/{{ username }}/category/{{ category.2 }}">{{ category.0 }}({{ category.1 }})</a>
                        </p>

                    {% endfor %}

                </div>
            </div>
            <div class="panel panel-danger">
                <div class="panel-heading">
                    <h3 class="panel-title">文章标签</h3>
                </div>
                <div class="panel-body">
                    {% for tag in tag_list %}
                        <p><a href="/{{ username }}/tag/{{ tag.2 }}">{{ tag.0 }}({{ tag.1 }})</a></p>
                    {% endfor %}
                </div>
            </div>
            <div class="panel panel-info">
                <div class="panel-heading">
                    <h3 class="panel-title">日期归档</h3>
                </div>
                <div class="panel-body">
                    {% for date in date_list %}
                        <p>
                            <a href="/{{ username }}/archive/{{ date.0|date:'Y-m' }}">{{ date.0|date:'Y年m月' }}({{ date.1 }})</a>
                        </p>
                    {% endfor %}
                </div>
            </div>
        </div>
        <div class="col-md-9">
            <ul class="media-list">
                {% for article_obj in article_lists %}
                    <li class="media">
                        <h4 class="media-heading"><a href="#">{{ article_obj.title }}</a></h4>
                        <div class="media-left">
                            <a href="#">
                                <img class="media-object" src="/media/{{ article_obj.blog.userinfo.avatar }}" alt="..."
                                     width="60">
                            </a>
                        </div>
                        <div class="media-body">
                            {{ article_obj.desc }}
                        </div>

                        <div class="pull-right">
                            <span>posted&nbsp;</span>
                            <span>&nbsp;&nbsp;</span>
                            <span>{{ article_obj.create_time|date:'Y-m-d' }}&nbsp;&nbsp;</span>
                            <span>{{ article_obj.blog.userinfo.username }}&nbsp;&nbsp;</span>
                            <span><span
                                    class="glyphicon glyphicon-comment"></span>评论({{ article_obj.comment_num }})&nbsp;&nbsp;</span>
                            <span><span
                                    class="glyphicon glyphicon-thumbs-up"></span>点赞({{ article_obj.up_num }})&nbsp;&nbsp;</span>
                            <span><a href="">编辑</a></span>
                        </div>
                    </li>
                    <hr>
                {% endfor %}

            </ul>
        </div>
    </div>
</div>
```

```python
re_path(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site)
```

```python
from django.db.models import Count
from django.db.models.functions import TruncMonth

def site(request, username, **kwargs):
    """

    :param request:
    :param username:
    :param kwargs: 如果该参数 有值，就需要对article_list做额外的筛选工作
    :return:
    """
    # 先校验当前用户名对应的个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 用户不存在返回一个404页面
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    # 查询当前站点下是所有文章
    article_lists = models.Article.objects.filter(blog=blog)
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 判断用户想要按照哪个条件筛选
        if condition == 'category':
            article_lists = article_lists.filter(category_id=param)
        elif condition == 'tag':
            article_lists = article_lists.filter(tags__id=param)
        else:
            year, month = param.split('-')

            article_lists = article_lists.filter(create_time__year=year, create_time__month=month)

    # 1.查询当前用户所有的分类及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_number=Count('article__pk')).values_list(
        'name', 'count_number','pk')
    # 2.查询当前所有用户的标签及标签下的标签数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_number=Count('article__pk')).values_list('name',
                                                                                                            'count_number','pk')
    # 3.按照年月统计所有的文章
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_number=Count('pk')).values_list('month', 'count_number')
    # print(data_list)
    return render(request, 'site.html', locals())

```

### 8、文章详情页

> 导航条，侧边栏不变，只有右侧区域在变化

```python
#url设计
/username/article/1

#先验证url是否会被顶替

#文章详情页和个人站点基本一致，所以用模板的继承
创建一个base.html,复制site.html的代码，在  <div class="col-md-9">这里划分区域，
     <div class="col-md-9">
            <!--文章数据展示区域-->
            {% block content %}
              
            {% endblock %}
        </div>
 然后把site.html中 的代码删除，直接继承



#site.html
{% extends 'base.html' %}

{% block content %}
    <ul class="media-list">
        {% for article_obj in article_list %}
            <li class="media">
                <h4 class="media-heading"><a href="">{{ article_obj.title }}</a></h4>
                <div class="media-left">
                    <a href="#">
                        <img class="media-object" src="/media/{{ article_obj.blog.userinfo.avatar }}" alt="..."
                             width='50px'>
                    </a>
                </div>
                <div class="media-body">
                    {{ article_obj.desc }}
                </div>

                <div class="pull-right">
                    <span>posted&nbsp;&nbsp;</span>
                    <span>@&nbsp;&nbsp;</span>
                    <span>{{ article_obj.create_time|date:'Y-m-d' }}&nbsp;&nbsp;</span>
                    <span>{{ article_obj.blog.userinfo.username }}&nbsp;&nbsp;</span>
                    <span><span class="glyphicon glyphicon-comment"></span>评论({{ article_obj.comment_num }})&nbsp;&nbsp;</span>
                    <span><span
                            class="glyphicon glyphicon-thumbs-up"></span>点赞({{ article_obj.up_num }})</span>
                    <span><a href="#">编辑</a></span>
                </div>
            </li>
            <hr>
        {% endfor %}

    </ul>
{% endblock %}

```

**给文章标题配置url,让其能够跳转**

```html
<!---site.html--->
<h4 class="media-heading"><a href="/{{ username }}/article/{{ article_obj.pk }}/">{{ article_obj.title }}</a></h4>

<!--home.html--->
<h4 class="media-heading"><a href="/{{ article_obj.blog.userinfo.username }}/article/{{ article_obj.pk }}/">{{ article_obj.title }}</a></h4>

```

**article_detail.html**

前端

```html
{% extends 'base.html' %}

{% block content %}
    <h1>{{ article_obj.title }}</h1>
    <div class="article_content|safe">
    {{ article_obj.content }}
    </div>
{% endblock %}
```

后端

```python
def article_detail(request, username, article_id):
    user_obj=models.UserInfo.objects.filter(username=username).first()
    blog=user_obj.blog
    # 先获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id,blog__userinfo__username=username).first()
    if not article_obj:
        return render(request,'error.html')
    return  render(request,'article_detail.html',locals())

```



#### **侧边栏inclusion_tag制作**

```python
#侧边栏的渲染需要传入数据，才能渲染，并且该侧边栏再很多个页面都需要使用
	1.那个地方用，就考呗代码
    2.将侧边栏制作成inclusion_tag
    """
    三步骤:
    	1.应用下名字必须为templatetags文件夹
    	2.该文件夹下创建任意名字的py文件
    	3.再该py文件内先固定书写两行代码
    		from django import template
    		register=template.Library()
    		#自定义过滤器
    		#定义标签
    		#定义inclusion_tag
    """
    
```



```python
#mytag.py
from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()


# 自定义inclusion_tag
@register.inclusion_tag('left_menu.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog

    # 构造侧边栏需要的数据
    # 1.查询当前用户所有的分类及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_number=Count('article__pk')).values_list(
        'name', 'count_number', 'pk')
    # 2.查询当前所有用户的标签及标签下的标签数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_number=Count('article__pk')).values_list('name',
                                                                                                            'count_number',
                                                                                                            'pk')
    # 3.按照年月统计所有的文章
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_number=Count('pk')).values_list('month', 'count_number')
    # print(data_list)
    return locals()
```

**letf_menu.html**

> 把base.html中<div class="col-md-3">里的代码剪切走，复制到left_menu.html中即可

```html
<div class="panel panel-primary">
    <div class="panel-heading">
        <h3 class="panel-title">文章分类</h3>
    </div>
    <div class="panel-body">
        {% for category in category_list %}
            <p><a href="/{{ username }}/category/{{ category.2 }}">{{ category.0 }}({{ category.1 }})</a></p>
        {% endfor %}
    </div>
</div>
<div class="panel panel-danger">
    <div class="panel-heading">
        <h3 class="panel-title">文章标签</h3>
    </div>
    <div class="panel-body">
        {% for tag in tag_list %}
            <p><a href="/{{ username }}/tag/{{ tag.2 }}">{{ tag.0 }}({{ tag.1 }})</a></p>
        {% endfor %}
    </div>
</div>
<div class="panel panel-info">
    <div class="panel-heading">
        <h3 class="panel-title">日期归档</h3>
    </div>
    <div class="panel-body">
        {% for date in date_list %}
            <p><a href="/{{ username }}/archive/{{ date.0|date:'Y-m' }}">{{ date.0|date:'Y年m月' }}({{ date.1 }})</a>
            </p>
        {% endfor %}

    </div>
</div>
```

**base.html**

```html
 <div class="col-md-3">
      {# 侧边栏区域#}
     
     {% load mytag %}
    {% left_menu username %}
     
        </div>
```

**后端**

```python
def article_detail(request, username, article_id):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 先获取文章对象，
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()

    if not article_obj:
        return render(request, 'error.html')
    # 获取当前文章所有的内容
    comment_list = models.Comment.objects.filter(article=article_obj)

    return render(request, 'article_detail.html', locals())
```

#### 文章点赞点踩

```python
"""
浏览器上看到的华丽花哨的内容，内部都是HTML(前端)代码

如何拷贝文章
	copy outerhtml
拷贝点赞点踩
	1.拷贝前端点赞点踩图标，html代码
	2.css样式也得拷
		由于有图片防盗链，所以将图片直接下载到本地
如何区分用户是点赞了还是点踩了
	1.给标签各自绑定一个事件
		两个标签对应的 代码基本一致，仅仅是 是否点赞点踩这一个参数不一致
	2.二合一
		给两个标签绑定一个事件
		 //给所有action类绑定事件
		   $('.action').click(function () {
                alert($(this).hasClass('diggit'))
            })
            
            
由于点赞点踩内部有一定的业务逻辑，所以后端单独开设视图函数处理
"""



# 前端页面
	1.拷贝博客园点赞点踩前端样式
        html代码 + css代码
    2.如何区分用户是点赞了还是点踩了
    	恰巧页面上有两个图标，所以给两个图标添加一个公共样式类
        然后给这个样式类绑定点击事件
        再利用this指代的就是当前被操作对象，利用hasClass判断是否有某个特定的类属性，从而判断出到底是两个图标中的哪一个
    
    3.书写ajax代码朝后端提交数据
    
    4.后端逻辑书写完毕后，前端针对点赞点踩动作实现需要动态展示提示信息
    	1.前端点赞点踩数字自增1，需要注意数据类型的问题
        	Number(old_num)+1
        2.用户没有登录，需要展示登录提示，并且登录可以条状 
        html()
        |safe()
        mark_safe()
#后端逻辑
	1.先判断用户是否登录
  	  request.user.authenticated()
    2.再判断当前文字是都是当前用户自己写的
    	通过文章主键值获取文章对象
        之后利用orm查询获取文章对象对应的用户对象与request.user比对
    3.判断当前用户是否已经给当前文章点了
    	利用article_obj文章对象和request.user用户对象去点赞点菜表中筛选数据，如果有数据则点过，没有则没点
    4.操作数据库，同时操作两张表
     	#前端发过来的是否点赞是一个字符串，需要自己转成布尔值活着利用字符串判断
       is_up=json.loads('is_up')
   		F查询
 """
 总结:再书写较为复杂的业务逻辑的时候，可以先按照一条线书写下去，之后再去弥补其他线路情况
 	类似于先走树的主干，之后再走分支
 
 """       
        
        
    
   
```



**前端**

在base.html中划分css和js区域

```html
{% block css %}

{% endblock %}


{% block js %}

{% endblock %}
```



```html



<!------article_detail.html------->

{% extends 'base.html' %}
{% block css %}
    <style>
        #div_digg {
            float: right;
            margin-bottom: 10px;
            margin-right: 30px;
            font-size: 12px;
            width: 125px;
            text-align: center;
            margin-top: 10px;
        }

        .diggit {
            float: left;
            width: 46px;
            height: 52px;
            background: url('/static/imgs/upup.gif') no-repeat;
            text-align: center;
            cursor: pointer;
            margin-top: 2px;
            padding-top: 5px;
        }

        .buryit {
            float: right;
            margin-left: 20px;
            width: 46px;
            height: 52px;
            background: url('/static/imgs/downdown.gif') no-repeat;
            text-align: center;
            cursor: pointer;
            margin-top: 2px;
            padding-top: 5px;
        }


        .clear {
            clear: both;
        }
    </style>
{% endblock %}


{% block content %}
<h1>{{ article_obj.title }}</h1>
<div class="article_content">
        {{ article_obj.content|safe }}
</div>
{#    点赞点踩图标样式开始#}
<div class="clearfix">
    <div id="div_digg">
        <div class="diggit action">
            <span class="diggnum " id="digg_count">{{ article_obj.up_num }}</span>
        </div>
        <div class="buryit action">
            <span class="burynum" id="bury_count">{{ article_obj.down_num }}</span>
        </div>
        <div class="clear"></div>
        <div class="diggword" id="digg_tips" style="color: red">
        </div>
    </div>
</div>
{#    点赞点踩图标样式结束#}
{% endblock %}
```

```js
//给所有action类绑定事件
$('.action').click(function () {
    let isUp = $(this).hasClass('diggit');
    let $div = $(this);
    //朝后端发送ajax
    $.ajax({
        url: '/up_or_down/',
        type: 'post',
        data: {
            'article_id': '{{ article_obj.pk }}',
            'is_up': isUp,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function (args) {
            if (args.code == 1000) {
                $('#digg_tips').text(args.msg)

                //将前端的数字加1
                let oldNum = $div.children().text();//文本是字符类型
                {#$btn.children().text(oldNum + 1 ) //字符串拼接#}
                $div.children().text(Number(oldNum) + 1) //字符串拼接

            } else {
                $('#digg_tips').html(args.msg)

            }
        }
    })
})
```

**后端**

```python
def up_or_down(request):
    """
    1.校验用户是否登录
    2.判断当前是否是当前用户自己写的，自己不能给自己 点赞
    3.当前用户是否已经给当前用户点过了
    4.操作数据库
    :param request:
    :return:
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        # 1.判断当前用户是否登录
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            # print(is_up,type(is_up)) true <class 'str'>
            is_up = json.loads(is_up)  # 把json格式的字符串true,转成python的布尔值true
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
                        # 给点踩数加1
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
```

#### 文章评论

```python
#根评论
    先把整体的评论功能跑通，再去填补
    1.书写前端获取用户评论的标签
        可能点赞点踩有浮动带啦的影响
            clearfix
  	2.点击评论按钮发送Ajax请求
    
    3.后端对评论单独开设url，处理
    后端逻辑其实非常的简单非常少
    
    4.针对根评论设计到前端的两种渲染方式
    	1.DOM操作临时渲染评论楼
        	需要用到模板字符
             //临时渲染评论列表
                        let userName = '{{ request.user.username }}';
                        let temp = `
                        <li class="list-group-item">
                            <span>${username}</span>
                            <span><a href="" class="pull-right">回复</a></span>
                            <div>
                               ${conTent}
                            </div>
                        </li>`
         2.页面刷新永久(render)渲染
        	后端直接获取当前文章所有评论，传递给html页面即可
            前端利用for循环参考博客园样式渲染评论
            
       	 3.	评论框里面的内容需要清空
#子评论
从回复按钮入手
    点击回复按钮发生了那些事：
    1.评论框自动聚焦.focus()
    2.评论框里自动添加对应评论的评论人
    	@username\n
    思考：根评论和子评论点的是同一个按钮
    	根评论和子评论的区别:
            其实之前的ajax代码只需要添加一个父评论id即可
    点击恢复按钮之后，应该获取到根评论对应的用户名和主键值
    针对主键值，多个函数都需要用，所以利用全局的变量形式存储
    针对子评论内容，需要切割出不是用户写的 @username\n
    
          //获取用户评论内容
            let conTent = $('#id_comment').val()
            //判断当前评论是否是子评论，如果是，需要将
            if (parentId) {
                //先找到\n对应的索引值， 然后利用切片，但是切片顾头不顾尾，所以要索引+1
                let indexNum = conTent.indexOf('\n') + 1;
                conTent = conTent.slice(indexNum);//将indexNum之前的所有数据切除，只保留后面的部分

            }
      后端parent_id字段本来就就可以位空，传不传值都可以直接存储数据
    
   		前端针对子评论渲染评论区的时候需要额外的判断
         <div>
             {#判断当前评论是否是子评论，如果是，要渲染对应的评论人名#}
                 {% if comment.parent_id %}
                 <p>@{{ comment.parent.user.username }}</p>
                 {% endif %}
                 {{ comment.content }}
          </div>
                            
      前端parent_id字段每次提交之后需要手动清空
          //清空全局的parentId
           parentId = null;
                      
```

**前端**

```html
{#    {{ 评论楼渲染开始 }}#}
<div>
    <ul class="list-group">

        {% for comment in comment_list %}
            <li class="list-group-item">
                <span>#{{ forloop.counter }}楼</span>
                <span>{{ comment.comment_time|date:'Y-m-d h:i:s' }}</span>
                <span>{{ comment.user.username }}</span>
                <span><a class="pull-right replay" username="{{ comment.user.username }}"
                         comment_id="{{ comment.pk }}">回复</a></span>

                <div>
                    {#                        判断当前评论是否是子评论，如果是，要渲染对应的评论人名#}
                    {% if comment.parent_id %}
                        <p>@{{ comment.parent.user.username }}</p>
                    {% endif %}
                    {{ comment.content }}
                </div>
            </li>
        {% endfor %}


    </ul>

</div>
{#    {{ 评论楼渲染结束 }}#}



{#    文章评论开始#}
{% if   request.user.is_authenticated %}
    <div>
        <p><span class="glyphicon glyphicon-comment"></span>发表评论</p>
        <div>
            <textarea name="comment" id="id_comment" cols="60" rows="10"></textarea>
        </div>
        <button class="btn btn-primary" id="id_submit">提交评论</button>
        <span style="color: red" id="error"></span>
    </div>
{% else %}
    <li><a href="{% url 'register' %}">注册</a></li>
    <li><a href="{% url 'login' %}">登录</a></li>
{% endif %}
{#    文章评论结束#}
```

```js
        //设置一个全局的parent_id
        let parentId = null
//用户点击评论按钮，发送ajax请求，
$('#id_submit').on('click', function () {
    //获取用户评论内容
    let conTent = $('#id_comment').val()
    //判断当前评论是否是子评论，如果是，需要将
    if (parentId) {
        //先找到\n对应的索引值， 然后利用切片，但是切片顾头不顾尾，所以要索引+1
        let indexNum = conTent.indexOf('\n') + 1;
        conTent = conTent.slice(indexNum);//将indexNum之前的所有数据切除，只保留后面的部分

    }
    $.ajax({
        url: '/comment/',
        type: 'post',
        data: {
            'article_id': '{{ article_obj.pk }}',
            'content': conTent,
            'parent_id': parentId,
            //如果parentId没有值，就是null，后端存储null没有任何问题
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function (args) {
            if (args.code == 1000) {
                $('#error').text(args.msg)
                //评论框里的内容清空
                $('#id_comment').val('')

                //临时渲染评论列表
                let userName = '{{ request.user.username }}';
                let temp = `
                <li class="list-group-item">
                    <span>${username}</span>
                    <span><a href="" class="pull-right">回复</a></span>
                    <div>
                       ${conTent}
                    </div>
                </li>`

                //将生成或的标签添加到url标签内
                $('.list-group').append(temp)
                //清空全局的parentId
                parentId = null;
            }
        }
    })
})




//给回复按钮绑定点击事件
$('.replay').click(function () {
    //需要评论对应的评论人姓名， 还需要评论人的主键值
    //获取用户名，
    let commentUsername = $(this).attr('username');
    //用户主键值 直接修改全局的变量名
    let parentId = $(this).attr('comment_id');
    //拼接信息塞给评论框
    $('#id_comment').val('@' + commentUsername + '\n').focus()
})
```

**后端**

```python
#评论功能
path('comment/',views.comment),
```

```python
def comment(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            if request.user.is_authenticated:
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id=request.POST.get('parent_id')
                # 直接操作评论表存储数据 两张表
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content,parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '用户未登录'

        return JsonResponse(back_dic)

```

### 9、后台管理

**前端**



```html
<!---backend/base.html--->

<div class="container-fluid">
    <div class="row">
        <div class="col-md-2">

            <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
                <div class="panel panel-default">
                    <div class="panel-heading" role="tab" id="headingOne">
                        <h4 class="panel-title">
                            <a role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseOne"
                               aria-expanded="true" aria-controls="collapseOne">
                                更多操作
                            </a>
                        </h4>
                    </div>
                    <div id="collapseOne" class="panel-collapse collapse in" role="tabpanel"
                         aria-labelledby="headingOne">
                        <div class="panel-body">
                            <a href="">添加文章</a>
                        </div>
                    </div>
                    <div id="collapseOne" class="panel-collapse collapse in" role="tabpanel"
                         aria-labelledby="headingOne">
                        <div class="panel-body">
                            <a href="">添加随笔</a>
                        </div>
                    </div>
                    <div id="collapseOne" class="panel-collapse collapse in" role="tabpanel"
                         aria-labelledby="headingOne">
                        <div class="panel-body">
                            <a href="">草稿箱</a>
                        </div>
                    </div>
                    <div id="collapseOne" class="panel-collapse collapse in" role="tabpanel"
                         aria-labelledby="headingOne">
                        <div class="panel-body">
                            <a href="">其他</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-10">

            <div>

                <!-- Nav tabs -->
                <ul class="nav nav-tabs" role="tablist">
                    <li role="presentation" class="active"><a href="#home" aria-controls="home" role="tab"
                                                              data-toggle="tab">文章</a></li>
                    <li role="presentation"><a href="#profile" aria-controls="profile" role="tab"
                                               data-toggle="tab">随笔</a>
                    </li>
                    <li role="presentation"><a href="#messages" aria-controls="messages" role="tab"
                                               data-toggle="tab">草稿</a>
                    <li role="presentation"><a href="#file" aria-controls="file" role="tab"
                                               data-toggle="tab">文件</a>

                    </li>
                    <li role="presentation"><a href="#settings" aria-controls="settings" role="tab"
                                               data-toggle="tab">设置</a>
                    </li>
                </ul>

                <!-- Tab panes -->
                <div class="tab-content">
                    <div role="tabpanel" class="tab-pane active" id="home">
                        {% block article %}

                        {% endblock %}
                    </div>
                    <div role="tabpanel" class="tab-pane" id="profile">随笔页面</div>
                    <div role="tabpanel" class="tab-pane" id="messages">草稿页面</div>
                    <div role="tabpanel" class="tab-pane" id="file">文件页面</div>
                    <div role="tabpanel" class="tab-pane" id="settings">设置页面</div>
                </div>

            </div>


        </div>
    </div>
</div>
</body>
</html>
```

```html
{% extends 'backend/base.html' %}

{% block article %}
    {#    接收当前用户 所有文章#}
    <table class="table-hover table-striped table">
        <thead>
        <tr>
            <th>标题</th>
            <th>评论数</th>
            <th>点赞数</th>
            <th>操作</th>
            <th>操作</th>
        </tr>
        </thead>
        <tbody>
        {% for article in page_queryset %}
            <tr>
                <td><a href="/{{ request.user.username }}/article/{{ article.pk }}">{{ article.title }}</a></td>
                <td>{{ article.comment_num }}</td>
                <td>{{ article.up_num }}</td>
                <td><a href="">编辑</a></td>
                <td><a href="">删除</a></td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
    <div class="pull-right">    {{ page_obj.page_html|safe }}</div>
{% endblock %}
```

**后端**

```python
#后台管理
path('backend/',views.backend),
```

```python
#添加分页器
from utils.mypage import Pagination


@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog)
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count())
    page_queryset=article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())
```

### 10、文章增查

**前端**

```html
{% extends 'backend/base.html' %}

{% block article %}
    <h3>添加文章</h3>
    {#    直接利用from表单提交数据#}
    <form action="" method="post">
        {% csrf_token %}
        <p>标题</p>
        <div>
            <input type="text" name="title" class="form-control">
        </div>
        <p>内容</p>
        <div>
            <textarea name="content" id="id_content" cols="30" rows="10"></textarea>
        </div>
        <p>分类</p>
        <div>
            {% for category in category_list %}
                <input type="radio" value="{{ category.pk }}" name="category">{{ category.name }}
            {% endfor %}
        </div>
        <p>标签</p>
        <div>
            {% for tag in tag_list %}
                <input type="checkbox" value="{{ tag.pk }}" name="tag">{{ tag.name }}
            {% endfor %}

        </div>
        <input type="submit" class="btn btn-danger">


    </form>
{% endblock %}
```

**前期后端代码**

```python
#添加文章
path('add/article/',views.add_article),
```

```python
def add_article(request):
    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)

    return render(request, 'backend/add_article.html',locals())
```

**后期后端代码**

```python
@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')

        # 文章简介
        # 1.先简单暴力的直接切取content  150个字符
        desc = content[0:150]
        article_obj = models.Article.objects.create(
            title=title,
            content=content,
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
```

#### 前端编辑器(kindeditor富文本编辑器)

[**KindEditor** 可视化 HTML 编辑器](https://www.oschina.net/p/kindeditor?hmsr=aladdin1e1)

[文档](http://kindeditor.net/doc.php)

```html
{% extends 'backend/base.html' %}

{% block article %}
    <h3>添加文章</h3>
    {#    直接利用from表单提交数据#}
    <form action="" method="post">
        {% csrf_token %}
        <p>标题</p>
        <div>
            <input type="text" name="title" class="form-control">
        </div>
        <p>内容</p>
        <div>
            <textarea name="" id="id_content" cols="30" rows="10"></textarea>
        </div>
        <p>分类</p>
        <div>
            {% for category in category_list %}
                <input type="radio" value="{{ category.pk }}" name="category">{{ category.name }}
            {% endfor %}
        </div>
        <p>标签</p>
        <div>
            {% for tag in tag_list %}
                <input type="checkbox" value="{{ tag.pk }}" name="tag">{{ tag.name }}
            {% endfor %}

        </div>
        <input type="submit" class="btn btn-danger">


    </form>

    {% block js %}
        {% load static %}
        <script charset="utf-8" src="{% static 'kindeditor-master/kindeditor-all-min.js' %}"></script>
        {#        <script charset="utf-8" src="/editor/lang/zh-CN.js"></script>#}
        <script>
            KindEditor.ready(function (K) {
                window.editor = K.create('#id_content', {
                    width: '100%',
                    height: '600px',
                    items: [
                        'source', '|', 'undo', 'redo', '|', 'preview', 'print', 'template', 'code', 'cut', 'copy', 'paste',
                        'plainpaste', 'wordpaste', '|', 'justifyleft', 'justifycenter', 'justifyright',
                        'justifyfull', 'insertorderedlist', 'insertunorderedlist', 'indent', 'outdent', 'subscript',
                        'superscript', 'clearhtml', 'quickformat', 'selectall', '|', 'fullscreen', '/',
                        'formatblock', 'fontname', 'fontsize', '|', 'forecolor', 'hilitecolor', 'bold',
                        'italic', 'underline', 'strikethrough', 'lineheight', 'removeformat', '|', 'image', 'multiimage',
                        'flash', 'media', 'insertfile', 'table', 'hr', 'emoticons', 'baidumap', 'pagebreak',
                        'anchor', 'link', 'unlink', '|', 'about'
                    ],
                    resizeType: 1,
                })
            });
        </script>
    {% endblock %}
{% endblock %}
```

### 10、处理XSS攻击以及文章摘要的处理

```pytohn
针对用户直接编写的html代码的网址
针对用户直接书写script标签，需要处理
	1.注释标签内部的内容
	2.直接将script删除
如何解决
	针对1 后端通过正则表达式筛选
	针对2 首相需要确定及获取script标签
	
	bs4模块，beautifulsoup模块
	专门用来处理html页面
	专门用于爬虫程序
	
```

```python
"""bs4模块使用"""
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
```

### 11、编辑器上传图片

```python
"""
别人写好了接口，但是接口不是你写的，
需要自己手动修改
"""
```

### 12、修改用户头像

### 13、总结

```python
#主要功能总结:
	表设计 开发流程
    注册功能
    	forms组件使用
        头像动态展示
        错误信息提示
    登录功能
    	图片验证码
        滑动验证码
    首页展示
    	media配置
        主动暴露任意资源接口
    个人站点展示
    	侧边栏展示
        侧边栏筛选
        侧边栏inclusion_tag
    文章详情页
    	点赞点踩
        评论
    后台管理
"""
针对BBS需要掌握每个功能的书写思路，内部逻辑
只够再去敲代码熟悉，找感觉
"""
```

