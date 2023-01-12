"""BBS URL Configuration
 n
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, re_path
from app01 import views
# 暴露后端指定文件夹资源
# 在暴露资源的时候，一定要明确该资源是否可以暴露
from django.views.static import serve
from BBS import settings  # 项目下的settings.py文件

urlpatterns = [
    # 点赞点踩
    path('up_or_down/', views.up_or_down),
    # 评论
    path('comment/', views.comment),
    # 后台管理
    path('backend/', views.backend),
    #添加文章
    path('add/article/',views.add_article),
    #编辑器上传图片接口
    path('upload_image/',views.upload_image),
    #修改用户头像
    path('set/avatar/',views.set_avatar),
    # 固定代码,开设后端指定资源
    re_path(r'media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('', views.login, name='login'),
    # 图片验证码相关
    path('get_code/', views.get_code, name='code'),
    # 首页
    path('home/', views.home, name='home'),
    # 修改密码
    path('set_password/', views.set_password, name='set_password'),
    # 退出登录
    path('logout/', views.logout, name='logout'),
    # 个人站点页面搭建
    re_path(r'^(?P<username>\w+)/$', views.site, name='site'),
    # 侧边栏筛选功能
    re_path(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site),
    # 文章详情页
    re_path(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail),
]
