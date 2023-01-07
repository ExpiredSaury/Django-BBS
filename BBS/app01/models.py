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