# -*- coding: UTF-8 -*- 
# @Date ：2023/1/11 21:25
from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()


@register.inclusion_tag('left_menu.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 1.查询当前用户所有的分类及分类下的文章个数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name',
        'count_num', 'pk')
    # 2.查询当前所有用户的标签及标签下的标签数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name',
        'count_num', 'pk')
    # 3.按照年月统计所有的文章
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_number=Count('pk')).values_list('month', 'count_number')
    return locals()
