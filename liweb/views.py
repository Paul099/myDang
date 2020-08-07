from django.shortcuts import render

from decimal import *

from django.shortcuts import render
import json
from django.http.response import HttpResponse, JsonResponse
from liweb.models import *      #把liweb模块的models引入
from datetime import datetime
import datetime
from django.db.models import Count

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


def ResponslibityDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                           “data” : {
    #     "role": "信息学院党支部书记",
    #     "role_resp_num": "25",
    #     "role_obs_num": "23",
    #     "party_branch": "信息学院党支部",
    #     "par_resp_num": "23",
    #     "par_obs_num": "24"
    #
    # }
    # }
   if request.method == "POST":
        userid = request.POST.get('user_id')
        code = request.POST.get('code')
        u= UserInfo.objects.filter(id=userid,)
        # book_list = models.Book.objects.all().annotate(author_num=Count("author"))
        #role_resp_num= RespList.objects.filter(userid).count()  统计数量1.可能直接统计relation表的id数量2.可能需要Select出Resplist之后，统计个数
        role_resp_num = RespRoleRelation.objects.filter(userid).count()
        role_obs_num= ObserRoleRelation.objects.filter(userid).Count()
        par_resp_num= PartyUserRelation.objects.filter(userid).count()
        par_obs_num= ObserPartyRelation.objects.filter(userid).count()

        response = {}
        if u.exists():

            response['message']='查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            #data = {'content': u[0].url}
            data = {'role': u[0].role,
                    'role_resp_num':role_resp_num,
                    'role_obs_num':role_obs_num,
                    'party_branch':u[0].part_branch,
                    'par_resp_num':par_resp_num,
                    'par_obs_num':par_obs_num,
                    }

        else:
            response['message'] = '查询失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] =data

        return HttpResponse(json.dumps(response), content_type="application/json")

   else:

        return HttpResponse("请用post方式访问")





def ResponslibitylistscDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"查询成功"
    #                           "data":{

    #     "party_branch": "信息学院党支部",
    #     "par_resp ": "XXXXXX",
    #     "par_obs ": "XXXXXXXXXXX"
    #
    # }
    if request.method == "POST":
        userid = request.POST.get('user_id')
        code= request.POST.get('code')
        u = UserInfo.objects.filter(id=userid)
        response = {}
        if u.exists():

            response['message'] = '查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            # data = {'content': u[0].url}
            data = {'party_branch': u[0].party_branch,
                    'par_resp': u[0].content,
                    'par_obs': u[0].observation_point,
                    }

        else:
            response['message'] = '查询失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")
