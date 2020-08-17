from django.shortcuts import render

from decimal import *

from django.shortcuts import render
import json
from django.http.response import HttpResponse, JsonResponse
from liweb.models import *  #把liweb模块的models引入
from datetime import datetime
import datetime
from django.db.models import Count,Max
import random
import string




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

#3--1.责任数据统计接口
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





#3--2.单位责任清单接口
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
        #p_o = PartyBranch.objects.filter(id=u[0].partyuserrelation_set.first().party_branch.id)
        p_o = ObservationList.objects.filter(obserpartyrelation__party__id=u[0].partyuserrelation_set.first().party_branch.id)
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
                    'par_obs': p_o[0].observation_point,
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



#3--3.学校责任清单接口
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








#5--1、会议数据统计接口
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
        m = MeetingUserRelation.objects.filter(user_id=userid,answer_id=2)

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








#5--2、会议列表查询接口
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
        departmentid= request.POST.get('department_id')
        taskstateid= request.POST.get('state_id')
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

        return HttpResponse(json.dumps(response,cls=CJsonEncoder), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")










#5--3、会议具体内容查询接口
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
                    'tz_user':list(u.values_list('user_name')),
                    'cj_user': list(u.filter(meetinguserrelation__answer=1).values_list('user_name')),
                    'qj_user':list(u.filter(meetinguserrelation__answer=2).values_list('user_name')),#存在bug，answer=2的筛选不出？？？？
                    'answer':mu[0].answer.answer,
                    'content':t[0].content,

                    }

        else:
            response['message'] = '查询失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] = data

        return HttpResponse(json.dumps(response,cls=CJsonEncoder), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")




#5--4、增加会议接口
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
        #time = request.POST.get('time')#时间作为请求参数
        place = request.POST.get('place')
        sponsor = request.POST.get('sponsor')
        type = request.POST.get('type')
        state =request.POST.get('state')
        userid = request.POST.get('user_id')
        content = request.POST.get('content')#对于存在的id可能无法添加？？？？
        response = {}

        d_idmax = Department.objects.aggregate(idmax=Max('id'))
        d = Department.objects.create(id =d_idmax['idmax']+1,name=department)
        d.save()

        m_idmax = Meeting.objects.aggregate(idmax=Max('id'))
        m = Meeting.objects.create(id=m_idmax['idmax']+1,theme=theme,place=place,sponsor =sponsor,)#time=time,)
        m.save()

        u = UserInfo.objects.create(id = userid,department_id=d_idmax['idmax']+1)
        u.save()

        tt_idmax = TaskType.objects.aggregate(idmax=Max('id'))
        tt = TaskType.objects.create(id=tt_idmax['idmax']+1,type=type)
        tt.save()

        ts_idmax = TaskState.objects.aggregate(idmax=Max('id'))
        ts = TaskState.objects.create(id=ts_idmax['idmax'] + 1, state=state)
        ts.save()

        t_idmax = Task.objects.aggregate(idmax=Max('id'))
        t = Task.objects.create(id=t_idmax['idmax']+1,content=content,state_id=ts_idmax['idmax'] + 1,type_id=tt_idmax['idmax']+1)
        t.save()

        um_idmax =MeetingUserRelation.objects.aggregate(idmax=Max('id'))
        um =MeetingUserRelation.objects.create(id=um_idmax['idmax']+1,meeting_id=m_idmax['idmax']+1,user_id=userid)
        um.save()

        ut_start = TaskUserRelation.objects.count()
        ut_idmax =TaskUserRelation.objects.aggregate(idmax=Max('id'))
        ut =TaskUserRelation.objects.create(id=ut_idmax['idmax']+1,task_id=t_idmax['idmax']+1,user_id=userid)
        ut.save()
        ut_end =TaskUserRelation.objects.count()




        if ut_start <ut_end:

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

        return HttpResponse(json.dumps(response,), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")









#5--5、邀请参会人接口
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

        mu =MeetingUserRelation.objects.filter(user_id=userid,meeting_id=meetingid)

        response = {}
        if  mu.exists() :

            response['message'] = '该用户已被邀请'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        else :

            m = MeetingUserRelation(user_id=userid, meeting_id=meetingid)
            m.save()
            response['message'] = '邀请成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'is succeed':1

                    }


        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")




#5--6、会议查询接口
def ManagamentQueryDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"签到成功"
    #                           "data":{
    #              'is succeed':1
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        userid = request.POST.get('user_id')


        m = Meeting.objects.filter(meetinguserrelation__user_id=userid).values('meetinguserrelation__meeting_id','theme')





        response = {}
        response['message'] = '签到成功'
        response['flag'] = 'true'
        response['code'] = 20000
        response['data'] = list(m)

        return HttpResponse(json.dumps(response), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")





#5--7、会议签到显示二维码接口（前端生成）
def ManagamentShowtoDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"签到成功"
    #                           "data":{
    #              'is succeed':1
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        meetingid = request.POST.get('meeting_id')

        m = Meeting.objects.filter(id=meetingid)
        m_v =[str(m[0].id )+ str(m[0].sponsor )+str(m[0].time)+str(m[0].theme)+str(m[0].place)+str(m[0].ratifier_field_id)]
        rad1 = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        rad2 = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        st = [rad1+m_v[0]+rad2]

        response = {}
        if m.exists() :

            response['message'] = '二维码获取成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'string':st[0]

                    }

        else:
            response['message'] = '二维码获取失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")




#5--8、会议签到用户扫码接口
def ManagamentShowinDoApi(request):
    # {
    #     "code":"20000"
    #              "flag":"true"
    #                    "message":"签到成功"
    #                           "data":{
    #              'is succeed':1
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        vxcode = request.POST.get('vx_code')
        #time = request.POST.get('time')  #请求参数里面包含time  格式不对
        place = request.POST.get('place')
        meetingid = request.POST.get('meeting_id')

        userid = UserInfo.objects.filter(vx_code=vxcode)
        m = Meeting.objects.filter(meetinguserrelation__user_id=userid[0].id,place=place,id=meetingid)#time=time





        response = {}
        if m.exists() :

            response['message'] = '签到成功'
            response['flag'] = 'true'
            response['code'] = 20000
            data = {'is succeed':1

                    }

        else:
            response['message'] = '签到失败'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

        response['data'] = data

        return HttpResponse(json.dumps(response), content_type="application/json")

    else:

        return HttpResponse("请用post方式访问")

