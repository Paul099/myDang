from decimal import *
from django.http.response import HttpResponse, JsonResponse
from liweb.models import *  #把liweb模块的models引入
from datetime import datetime
from django.db.models import Count,Max,Q
import  json,time,hashlib,string,random,datetime
from django.core import signing
from django.core.cache import cache
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage




# #-----------------分页--------------------#
#实现对不符合要求的页数的处理
# def process_paginator(request, article_list):
#     #每一页要显示的记录数
#     paginator = Paginator(article_list, 10)
#     try:
#         page_number = int(request.GET.get('page', '1'))
#         page = paginator.page(page_number)
#     except (PageNotAnInteger, EmptyPage, InvalidPage):
#         page = paginator.page(1)
#     return page


#-----------------Token------------------#
HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'CHEN_FENG_YAO'
SALT = 'www.lanou3g.com'
TIME_OUT = 30 * 60  # 30min


def encrypt(obj):
    """加密"""
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def decrypt(src):
    """解密"""
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    print(type(raw))
    return raw


def create_token(username):
    """生成token信息"""
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload
    payload = {"username": username, "iat": time.time()}
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 存储到缓存中
    cache.set(username, token, TIME_OUT)
    return token


def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


# 通过token获取用户名
def get_username(token):
    payload = get_payload(token)
    return payload['username']
    pass


def check_token(token):
    username = get_username(token)
    last_token = cache.get(username)
    if last_token:
        return last_token == token
    return False



#---------------时间格式---------------#
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

#----------------接口---------------#
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
        token = request.POST.get('token')
        userid = request.POST.get('user_id')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
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


            paginator = Paginator(data, 5)#预计实现分页#参数1返回的数据，参数2每页数据数
            page_x = paginator.page(1)
            response['total'] = paginator.count
            response['data'] = page_x.object_list#list(data)


            response['data'] =data
            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code":code,"message": "请登录"}), content_type="application/json")

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
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            userid = request.POST.get('user_id')

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
            return HttpResponse(json.dumps({"code":code,"message": "请登录"}), content_type="application/json")

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
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            userid = request.POST.get('user_id')
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
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

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
        token =request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            userid = request.POST.get('user_id')
            u = UserInfo.objects.filter(id=userid)
            m = MeetingUserRelation.objects.filter(user_id=userid,answer_id=None)
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
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")


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
    #               "state": "未完成"
    # }
    if request.method == "POST":
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            userid = request.POST.get('user_id')
            departmentid= request.POST.get('department_id')
            taskstateid= request.POST.get('state_id')
            m_set = MeetingUserRelation.objects.filter(user_id=userid,
                                                       user__task__state_id=taskstateid,
                                                       user__department_id=departmentid).values('meeting_id',
                                                                                                'meeting__theme',
                                                                                                'user__department__name',
                                                                                                'meeting__time',
                                                                                                'meeting__place',
                                                                                                'meeting__sponsor__user_name', #因为sponsor修改为user的外键，需要跨表查询名字
                                                                                                'meeting__meeting_type__meeting_type',#添加了type表，需要查询跨表
                                                                                                'user__task__state__state',
                                                                                                ).distinct()
            response = {}
            if m_set.exists():

                response['message'] = '查询成功'
                response['flag'] = 'true'
                response['code'] = 20000
                data = m_set

            else:
                response['message'] = '查询失败'
                response['flag'] = 'flase'
                response['code'] = 40000
                data = {}

            response['data'] = list(data)
            return HttpResponse(json.dumps(response,cls=CJsonEncoder), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

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
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            meetingid = request.POST.get('meeting_id')

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
                        'sponsor':m[0].sponsor.user_name,#修改了sponsor的查询方式
                        'type':t[0].type.type,
                        'state':t[0].state.state,
                        'tz_user':list(u.values_list('user_name')),
                        'cj_user': list(u.filter(meetinguserrelation__answer=1).values_list('user_name')),
                        'qj_user':list(u.exclude(meetinguserrelation__answer=1).values_list('user_name')),
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
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

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
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            theme = request.POST.get('theme')
            department = request.POST.get('department')
            time = request.POST.get('time')#时间作为请求参数？？？？
            place = request.POST.get('place')
            sponsor = request.POST.get('sponsor')
            type = request.POST.get('type')
            state =request.POST.get('state')
            userid = request.POST.get('user_id')
            content = request.POST.get('content')

            #d_idmax = Department.objects.aggregate(idmax=Max('id'))
            #d = Department.objects.create(id =d_idmax['idmax']+1,name=department)
            d = Department.objects.create( name=department)
            d.save()
            m = Meeting.objects.create( theme=theme, place=place, sponsor_id=sponsor, time=time, )
            m.save()
            u = UserInfo.objects.create(id = userid,department_id=d.id)
            u.save()
            tt = TaskType.objects.create( type=type)
            tt.save()
            ts = TaskState.objects.create(state=state)
            ts.save()
            t = Task.objects.create( content=content, state_id=ts.id,type_id=tt.id)
            t.save()
            um = MeetingUserRelation.objects.create( meeting_id=m.id,user_id=userid)
            um.save()

            ut_start = TaskUserRelation.objects.count()
            ut = TaskUserRelation.objects.create( task_id=t.id, user_id=userid)
            ut.save()
            ut_end =TaskUserRelation.objects.count()

            response = {}
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
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

    else:
        return HttpResponse("请用post方式访问")









# #5--5、邀请参会人接口
# def ManagamentInviteDoApi(request):
#     # {
#     #     "code":"20000"
#     #              "flag":"true"
#     #                    "message":"添加成功"
#     #                           "data":{
#     #              'is succeed':1
#     # }
#     if request.method == "POST":
#         token = request.POST.get('token')
#         code = request.POST.get('code')
#         if check_token(token):
#             meetingid = request.POST.get('meeting_id')
#             userid = request.POST.get('user_id')
#
#             mu =MeetingUserRelation.objects.filter(user_id=userid,meeting_id=meetingid)
#             response = {}
#             if  mu.exists() :
#
#                 response['message'] = '该用户已被邀请'
#                 response['flag'] = 'flase'
#                 response['code'] = 40000
#                 data = {}
#
#             else :
#
#                 m = MeetingUserRelation(user_id=userid, meeting_id=meetingid)
#                 m.save()
#                 response['message'] = '邀请成功'
#                 response['flag'] = 'true'
#                 response['code'] = 20000
#                 data = {'is succeed':1
#                         }
#             response['data'] = data
#             return HttpResponse(json.dumps(response), content_type="application/json")
#
#         else:
#             return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")
#
#     else:
#         return HttpResponse("请用post方式访问")
#




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
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            userid = request.POST.get('user_id')

            m = Meeting.objects.filter(meetinguserrelation__user_id=userid).values('meetinguserrelation__meeting_id','theme')

            response = {}
            response['message'] = '签到成功'
            response['flag'] = 'true'
            response['code'] = 20000
            response['data'] = list(m)

            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

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
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
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
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

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
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):

            current_page_num = request.POST.get('page')
            vxcode = request.POST.get('vx_code')
            place = request.POST.get('place')
            meetingid = request.POST.get('meeting_id')
            time = timezone.localtime()  #请求参数里面包含time  格式不对

            userid = UserInfo.objects.filter(vx_code=vxcode)
            m = Meeting.objects.filter(meetinguserrelation__user_id=userid[0].id,place=place,id=meetingid,time__gte=time)

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
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

    else:
        return HttpResponse("请用post方式访问")







#5--9、会议应答接口
def ManagamentAnswerDoApi(request):
    # {
    #     "is_succeed": "1"
    # }

    if request.method == "POST":
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):

            current_page_num = request.POST.get('page')
            userid = request.POST.get('user_id')
            answerid = request.POST.get('answer_id')
            meetingid = request.POST.get('meeting_id')
            reason = request.POST.get('reason')


            m_u = MeetingUserRelation.objects.filter(user_id=userid,meeting_id=meetingid,answer_id=None,reason=None)
            #m_u.update()更新应该在判断之后

            # m = Meeting.objects.filter(meetinguserrelation__user_id=userid[0].id,place=place,id=meetingid,time__gte=time)

            response = {}
            if m_u.exists() :
                m_u.update(answer_id=answerid,reason=reason)
                response['message'] = '应答成功'
                response['flag'] = 'true'
                response['code'] = 20000
                data = {'is succeed':1
                        }

            else:
                response['message'] = '应答失败'
                response['flag'] = 'flase'
                response['code'] = 40000
                data = {}

            response['data'] = data

            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

    else:
        return HttpResponse("请用post方式访问")






#5--10、会议类型查询接口
def ManagamentTypeDoApi(request):
    # {
    #     "meeting_type_id": "1",
    #     "meeting_type": "党建学习"
    # }
    # {
    #     " meeting_type_id ": "2",
    #     " meeting_type ": "任务总结"
    # }
    # ……
    if request.method == "POST":
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            m_t = MeetingType.objects.values('meeting_type_id','meeting_type')

            response = {}
            if m_t.exists() :

                response['message'] = '查询成功'
                response['flag'] = 'true'
                response['code'] = 20000
                data = m_t

            else:
                response['message'] = '查询失败'
                response['flag'] = 'flase'
                response['code'] = 40000
                data = {}

            response['data'] = list(m_t)

            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

    else:
        return HttpResponse("请用post方式访问")




# 6--1、用户查询接口
def UserInquireDoApi(request):
    # {
    #     "user_id ": "1",
    #     "name ": "王臣",
    #     "department_id": "1",
    #     "department_name": "信息学院"
    # }
    # {
    #     "user_id ": "2",
    #     "name ": "王宁",
    #     "department_id": "1",
    #     "department_name": "信息学院"
    # }
    # ……
    if request.method == "POST":
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            u = UserInfo.objects.values('id','user_name','department_id','department__name').order_by('id')

            response = {}
            if u.exists():

                response['message'] = '查询成功'
                response['flag'] = 'true'
                response['code'] = 20000
                data = u

            else:
                response['message'] = '查询失败'
                response['flag'] = 'flase'
                response['code'] = 40000
                data = {}

            paginator = Paginator(data, 5)#预计实现分页
            page_x = paginator.page(current_page_num)
            response['total'] = paginator.count
            response['data'] = page_x.object_list

            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code": code, "message": "请登录"}), content_type="application/json")

    else:
        return HttpResponse("请用post方式访问")


# 6--2、部门查询接口
def DepartmentInquireDoApi(request):
    # {
    #     "department_id": "1",
    #     "department_name": "信息学院"
    # }
    # {
    #     "department_id": "2",
    #     "department_name": "电气学院"
    # }
    # ……

    if request.method == "POST":
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):

            current_page_num = request.POST.get('page')
            d = Department.objects.values('id','name').order_by('id')
            page_x = Paginator(d, 5).page(number=current_page_num).object_list# current_page_num

            #response = {}
            if d.exists():
              response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "data": page_x#(page_x.object_list)
                }
            else:
                response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "data": {}
                }

            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code": code, "message": "请登录"}), content_type="application/json")

    else:
        return HttpResponse("请用post方式访问")


# current_pag_num = request.GET.get('page')
#paginator = Paginator(data, 5)
# page_x= paginator.page(number=current_pag_num)
# page_x.object_list
