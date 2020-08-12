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
            data = {'role': u[0].roleuserrelation_set.first().role.role,#一个user_id对应多个role时无法显示？？？？？？？
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






def ResponsLibitylistDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"查询成功"
    #                           "data":{

    #             "party_branch": "信息学院党支部",
    #             "par_resp ": "XXXXXX",
    #             "par_obs ": "XXXXXXXXXXX",
    #             "department": "信息学院",
    #             "dep_resp ": "XXXXXX",
    #             "dep_obs ": "XXXXXXXXXXX"
    #}

    if request.method == "POST":
        userid = request.POST.get('user_id')
        code = request.POST.get('code')
        u = UserInfo.objects.filter(id=userid)
        p_o = PartyBranch.objects.filter(id=u[0].partyuserrelation_set.first().party_branch.id)
        p_r = RespDepRelation.objects.filter(department_id=u[0].department.id)#part_resp 的问题没有解决
        d = Department.objects.filter(id=u[0].department.id)
        r = RoleInfo.objects.filter(id=u[0].roleuserrelation_set.first().role.id)

        response = {}
        if u.exists():

            response['message'] = '查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'party_branch': u[0].partyuserrelation_set.first().party_branch.party_branch,
                    'par_resp': p_r[0].resp.content,
                    'par_obs': p_o[0].obserpartyrelation_set.first().observation.observation_point,
                    'department':d[0].name,
                    'dep_resp':d[0].respdeprelation_set.first().resp.content,
                    'dep_obs':r[0].obserrolerelation_set.first().observation.observation_point,#连续跨表的department--obser?????
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









def ManagamentDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"查询成功"
    #                           "data":{
    #      "name": "李四",
    #      "meeting_num": "6",
    #      "wd_meeting_num": "2"

    # }

    if request.method == "POST":
        userid = request.POST.get('user_id')
        code= request.POST.get('code')
        u = UserInfo.objects.filter(id=userid)
        m = MeetingUserRelation.objects.filter(user_id=userid).filter(answer=2)

        response = {}
        if u.exists():

            response['message'] = '查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'name': u[0].user_name,
                    'meeting_num': u[0].meetinguserrelation_set.count(),
                    'wd_meeting_num':m.count(),
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









def ManagamentInquireDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"查询成功"
    #                           "data":{
    #               "meeting_id ": "1",
    #               "theme": "XXXXX",
    #               "department": "信息",
    #               "time": "2020-5-31",
    #               "place": "信息学院A307",
    #               "sponsor": "李四",
    #               "type": "XXXX",
    #               "state": "未完成"   #
    # }
    if request.method == "POST":
        userid = request.POST.get('user_id')
        code= request.POST.get('code')
        departmentid=request.POST.get('department_id')
        taskstateid=request.POST.get('state_id')
        t = Task.objects.filter(taskuserrelation__user_id=userid, state_id=taskstateid, department_id=departmentid)
        u = UserInfo.objects.filter(taskuserrelation__task__state_id=taskstateid, department_id=departmentid, id=userid)
        mu = MeetingUserRelation.objects.filter(user_id=u[0].id)
        m = Meeting.objects.filter(id=mu[0].meeting_id)



        response = {}
        if u.exists():

            response['message'] = '查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'meeting_id ': m[0].id,
                    'theme': m[0].theme,
                    'department':u[0].department.name,
                    'time':m[0].time,
                    'place':m[0].place,
                    'sponsor':m[0].sponsor,
                    'type':t[0].type.type,
                    'state':t[0].state.state
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











def ManagamentSpecificDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"查询成功"
    #                           "data":{
    #        "meeting_id ": "1",
    #         "theme": "XXXXX",
    #         "department": "信息",
    #        "time": "2020-5-31",
    #        "place": "信息学院A307",
    #        "sponsor": "李四",
    #         "type": "XXXX",
    #         "state": "未完成"
    #        "tz_user": "XXX,XXX,XXX,XXX",
    #        "cj_user": " XXX,XXX,XXX,XXX ",
    #       "qj_user": " XXX,XXX,XXX",
    #        "answer": "参加",
    #          "content": "XXXXX"

    # }

    if request.method == "POST":
        meetingid = request.POST.get('meeting_id')
        code= request.POST.get('code')
        m = Meeting.objects.filter(id=meetingid)
        d =Department.objects.filter(userinfo__meetinguserrelation__meeting_id=meetingid)
        u =UserInfo.objects.filter(meetinguserrelation__meeting_id=meetingid)
        t =Task.objects.filter(taskuserrelation__user_id=u[0].id)
        mu =MeetingUserRelation.objects.filter(meeting_id=meetingid)
        response = {}
        if m.exists():

            response['message'] = '查询成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'meeting_id': m[0].id,
                    'theme':m[0].theme,
                    'department':d[0].name,
                    'time':m[0].time,
                    'place':m[0].place,
                    'sponsor':m[0].sponsor,
                    'type':t[0].type.type,
                    'state':t[0].state.state,
                    'tz_user':u.values_list('user_name'),
                    'cj_user':u.filter(meetinguserrelation__answer_0=1).values_list('user_name'),
                    'qj_user':u.filter(meetinguserrelation__answer=2).values_list('user_name'),
                    'answer':mu[0].answer.answer,
                    'content':t[0].content

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





def ManagamentAddDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"添加成功"
    #                           "data":{
    #              'is succeed':1
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        theme = request.POST.get('theme')
        department = request.POST.get('department')
        time = request.POST.get('time')
        place = request.POST.get('place')
        sponsor = request.POST.get('sponsor')
        type = request.POST.get('type')
        userid = request.POST.get('user_id')
        content = request.POST.get('content')
        response = {}
        d = Department.objects.create(name=department)
        m = Meeting.objects.create(theme=theme,time=time,place=place,sponsor =sponsor,content=content,)
        u = UserInfo.objects.create(id = userid)
        t = TaskType.objects.create(type=type)

        if m|d|u|t.exists() :

            response['message'] = '添加成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'is succeed':1

                    }

        else:
            response['message'] = '添加失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")






def ManagamentInviteDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"添加成功"
    #                           "data":{
    #              'is succeed':1
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        meetingid = request.POST.get('meeting_id')
        userid = request.POST.get('user_id')

        v = MeetingUserRelation.objects.get(user_id=userid)
        v.meeting_id = meetingid
        v.save()



        response = {}
        if v.exists() :

            response['message'] = '邀请成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'is succeed':1

                    }

        else:
            response['message'] = '邀请失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")
