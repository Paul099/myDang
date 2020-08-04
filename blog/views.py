from decimal import *

from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse
from blog.models import *
from datetime import datetime
import datetime

class CJsonEncoder(json.JSONEncoder):
    # 转换datatime
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # 这里可以统一修改想要的格式
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            # 这里可以统一修改想要的格式
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(Decimal(obj).quantize(Decimal('0.0')))
        else:
            return json.JSONEncoder.default(self, obj)

def dictfetchall(cursor):
    # "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


# Create your views here.
def LoginApi(request):
    # {
    #     "code":"20000"
    #     "flag":"true"
    #     "message":"查询成功"
    #     "data":{
    #         "user_id ": "1",
    #         "department_id": "2",
    #         "token":"20000"
    #     }
    # }
    if request.method == "POST":
        username = request.POST.get('user_name')
        password = request.POST.get('password')
        u = UserInfo.objects.filter(user_name=username)
        response = {}
        if u.exists():
            if u[0].password != password:
                response['message']='用户或密码不正确'
                response['flag'] = 'flase'
                response['code'] = 40000
                data = {'token':40000}
            else:
                response['message'] = '登录正确'
                response['flag'] = 'true'
                response['code'] = 20000
                data = { 'department_id': u[0].department_id,'user_id': u[0].id,'token':20000}
        else:
            response['message'] = '用户名不存在'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {'token':40000}

        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def IndexDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "file_id ": "1",
    #     "title": "报告",
    #     "time": "2020-6-30"
    # }
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        u = FileInfo.objects.filter(file_type=1).values()
        response = {}

        response['message'] = '查询成功'
        response['flag'] = 'true'
        response['code'] = 20000



        response['data'] = list(u)

        return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")



def MostDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "content ": "XXXXXXXXX"
    # }
    # }
    if request.method == "POST":
        id = request.POST.get('id')
        code = request.POST.get('code')
        u = FileInfo.objects.filter(id=id,file_type=1)
        response = {}
        if u.exists():

            response['message']='查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'content': u[0].url}

        else:
            response['message'] = '查询失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def ListDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "file_id ": "1",
    #     "title": "报告",
    #     "ptime": "2020-6-30"
    # }
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        u = FileInfo.objects.filter(file_type=1).values()
        response = {}

        response['message'] = '查询成功'
        response['flag'] = 'true'
        response['code'] = 20000



        response['data'] = list(u)

        return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def WorkDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "content ": "XXXXXXXXX"
    # }
    # }
    if request.method == "POST":
        id = request.POST.get('id')
        code = request.POST.get('code')
        u = FileInfo.objects.filter(id=id,file_type=2)
        response = {}
        if u.exists():

            response['message']='查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'content': u[0].url}

        else:
            response['message'] = '查询失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")