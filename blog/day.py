from decimal import *
from blog.token_module import *
from django.db.models import Max, Avg
from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse
from blog.models import *
from datetime import datetime
import datetime
from django.core.paginator import Paginator
from itertools import chain

def DayToFinish():
    Task.objects.filter(end_time__lt=datetime.datetime.now()-datetime.timedelta(days=Overtime.objects.get().day_num)).update(state=TaskState(id=4))
    print(datetime.datetime.now().strftime('%Y-%m-%d')+"更新逾期数据成功")