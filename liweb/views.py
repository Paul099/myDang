from django.shortcuts import render

from decimal import *

from django.shortcuts import render
import json
from django.http.response import HttpResponse, JsonResponse
from liweb.models import *  #把liweb模块的models引入
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
        u= UserInfo.objects.filter(id=userid)
        r= RoleInfo.objects.filter(id=u[0].roleuserrelation_set.first().role.id)
        p= PartyBranch.objects.filter(id=u[0].partyuserrelation_set.first().party_branch.id)
        #par_resp_num= PartyUserRelation.objects.filter(userid).count()


        response = {}
        if u.exists():

            response['message']='查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'role': u[0].roleuserrelation_set.first().role.role,
                    'role_resp_num':r[0].resprolerelation_set.count(),
                    'role_obs_num':r[0].obserrolerelation_set.count(),
                    'party_branch':u[0].partyuserrelation_set.first().party_branch.party_branch,
                    'par_resp_num':p[0].partyuserrelation_set.count(),#没有Part_resp_relation表，无法明确确定党组织责任？？？？？
                    'par_obs_num':p[0].obserpartyrelation_set.count(),
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
        p_o = PartyBranch.objects.filter(id= u[0].partyuserrelation_set.first().party_branch.id)
        p_r = RespDepRelation.objects.filter(department_id=u[0].department.id)


        response = {}
        if u.exists():

            response['message'] = '查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'party_branch': u[0].partyuserrelation_set.first().party_branch.party_branch,
                    'par_resp': p_r[0].resp.content,
                    'par_obs': p_o[0].obserpartyrelation_set.first().observation.observation_point,
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
