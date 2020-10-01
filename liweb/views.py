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
def ResponsibilityDoApi(request):
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
            #current_page_num = request.POST.get('page')
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


            # paginator = Paginator(data, 5)#预计实现分页#参数1返回的数据，参数2每页数据数
            # page_x = paginator.page(1)
            # response['total'] = paginator.count
            # response['data'] = page_x.object_list#list(data)


            response['data'] =data
            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code":code,"message": "请登录"}), content_type="application/json")

   else:
        return HttpResponse("请用post方式访问")








#3--2.单位责任清单接口
def ResponsibilityListPartyDoApi(request):
    # [
    #     {
    #         "party_branch": "信息学院党支部",
    #         "par_resp ": "XXXXXX",
    #         "par_obs ": "XXXXXXXXXXX",
    #     }
    #     {
    #         "party_branch": "电子系党支部",
    #         "par_resp ": "XXXXXX",
    #         "par_obs ": "XXXXXXXXXXX",
    #     }
    # ……
    # ]

    if request.method == "POST":
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            current_page_size = request.POST.get('pagesize')
            userid = request.POST.get('user_id')


            pid = PartyBranch.objects.filter(Q(partyuserrelation__user_id=userid)&~Q(party_branch__startswith='校')).first().pid_id#通过 Q（__startswith='校'）筛选出不是校党委的支部的pid
            #pid= PartyBranch.objects.filter(partyuserrelation__user_id=userid).first().pid_id#)&~Q(party_branch__startswith='校')
            # p = PartyBranch.objects.filter(Q(partyuserrelation__user_id=userid)|Q(id= pid)).values('party_branch',
            #                                                                                        'resppartyrelation__resp__content',
            #                                                                                        'obserpartyrelation__observation__observation_point').distinct()
            partys = PartyBranch.objects.filter(Q(partyuserrelation__user_id=userid)|Q(id= pid)).distinct()
            partys_num = partys.count()
            p = []
            data = []
            for i in range(partys_num):  #空列表直接赋值失败，需要append
                p.append(i)
                data.append(i)
            for x  in range(partys_num):
                p[x] = PartyBranch.objects.filter(id=partys[x].id).distinct()
                data[x]= {'party_branch': p[x].first().party_branch,
                           'resppartyrelation__resp__content':list(p[x].values_list('resppartyrelation__resp__content')),
                           'obserpartyrelation__observation__observation_point':list(p[x].values_list('obserpartyrelation__observation__observation_point'))}

            paginator =Paginator(data,current_page_size)
            total = paginator.count
            page_x = paginator.page(number=current_page_num).object_list

            response = {}
            if partys.exists():
                response={
                    'message':'查询成功',
                    'flag':'true',
                    'code':20000,
                    'total':total,
                    'data':list(page_x)
                }
            else:
                response={
                    'message':'查询失败',
                    'flag':'flase',
                    'code':40000,
                    'data':{}
                }

            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code":code,"message": "请登录"}), content_type="application/json")

    else:
        return HttpResponse("请用post方式访问")


#3--3.我的责任清单接口
def ResponsibilityListRoleDoApi(request):
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
            current_page_size = request.POST.get('pagesize')
            userid = request.POST.get('user_id')

            # r = RoleInfo.objects.filter(roleuserrelation__user_id=userid).values('role',
            #                                                                      'resprolerelation__resp__content',
            #                                                                      'obserrolerelation__observation__observation_point').distinct()
            roles = RoleInfo.objects.filter(roleuserrelation__user_id=userid).distinct()
            roles_num = roles.count()
            r = []
            data = []
            for i in range(roles_num):  #空列表直接赋值失败，需要append
                r.append(i)
                data.append(i)
            for x  in range(roles_num):
                r[x] = RoleInfo.objects.filter(id=roles[x].id).distinct()
                data[x]= {'role': r[x].first().role,
                           'resprolerelation__resp__content':list(r[x].values_list('resprolerelation__resp__content')),
                           'obserrolerelation__observation__observation_point':list(r[x].values_list('obserrolerelation__observation__observation_point'))}






            paginator =Paginator(data,current_page_size)
            total = paginator.count
            page_x = paginator.page(number=current_page_num).object_list
            response = {}
            if roles.exists():
                response={
                    'message':'查询成功',
                    'flag':'true',
                    'code':20000,
                    'total':total,
                    'data':list(page_x)#data
                }

            else:
                response={
                    'message':'查询失败',
                    'flag':'flase',
                    'code':40000,
                    'data':{}
                }

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
            #current_page_num = request.POST.get('page')
            userid = request.POST.get('user_id')
            u = UserInfo.objects.filter(id=userid)
            m = MeetingUserRelation.objects.filter(user_id=userid,answer_id=None)
            response = {}
            if u.exists():

                response['message'] = '查询成功'
                response['flag'] = 'true'
                response['code'] = 20000
                data = {'name': u[0].name,
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
            current_page_size = request.POST.get('pagesize')
            userid = request.POST.get('user_id')
            departmentid= request.POST.get('department_id')
            #taskstateid= request.POST.get('state_id')
            stateid = request.POST.get('state_id')
            m_set = MeetingUserRelation.objects.filter(user_id=userid,
                                                       meeting__state_id=stateid,
                                                       user__department_id=departmentid).values('meeting_id',
                                                                                                'meeting__theme',
                                                                                                'user__department__name',
                                                                                                'meeting__time',
                                                                                                'meeting__place',
                                                                                                'meeting__sponsor__user_name', #因为sponsor修改为user的外键，需要跨表查询名字
                                                                                                'meeting__meeting_type__meeting_type',#添加了type表，需要查询跨表
                                                                                                'meeting__state__state',
                                                                                                ).distinct().order_by('id')
            paginator = Paginator(m_set,current_page_size)
            total = paginator.count
            page_x = paginator.page(number=current_page_num).object_list# current_page_num

            if m_set.exists():
              response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "total": total,
                    "data": list(page_x)#(page_x.object_list)
                }
            else:
                response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询失败",
                    "data": {}
                }

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
            #current_page_num = request.POST.get('page')
            meetingid = request.POST.get('meeting_id')

            m = Meeting.objects.filter(id=meetingid)
            #d =Department.objects.filter(id=m[0].department_id).first()
            u =UserInfo.objects.filter(meetinguserrelation__meeting_id=meetingid)
            mu =MeetingUserRelation.objects.filter(meeting_id=meetingid)

           # # m = Meeting.objects.filter(id= meetingid).values('department_id',
           #                                                   'theme',
           #                                                   'department__department__name',
           #                                                   'time',
           #                                                   'place',
           #                                                   'sponsor__user_name',
           #                                                   'meeting_type__meeting_type',
           #                                                   'state_id',
           #                                                   'content')
            response = {}
            if m.exists():

                response['message'] = '查询成功'
                response['flag'] = 'true'
                response['code'] = 20000
                data = {'meeting_id': m[0].id,
                        'theme':m[0].theme,
                        'department':m[0].department.name,
                        'time':m[0].time,
                        'place':m[0].place,
                        'sponsor':m[0].sponsor.user_name,#修改了sponsor的查询方式
                        'type':m[0].meeting_type.meeting_type,
                        'state':m[0].state_id,
                        'tz_user':list(u.values_list('user_name')),
                        'cj_user': list(u.filter(meetinguserrelation__answer=1).values_list('user_name')),
                        'qj_user':list(u.exclude(meetinguserrelation__answer=1).values_list('user_name')),
                        'answer':mu[0].answer.answer,
                        'content':m[0].content,
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
            #current_page_num = request.POST.get('page')
            theme = request.POST.get('theme')
            department = request.POST.get('department_id')
            time = request.POST.get('time')
            place = request.POST.get('place')
            sponsor = request.POST.get('sponsor')
            type = request.POST.get('type')
            stateid =request.POST.get('state_id')#########
            #userid = request.POST.get('user_id')#peoNames = request.POST.getlist('peoName', [])

            userid = request.POST.getlist('user_id[]')
            content = request.POST.get('content')######

            #d_idmax = Department.objects.aggregate(idmax=Max('id'))
            #d = Department.objects.create(id =d_idmax['idmax']+1,name=department)
            # d = Department.objects.create( name=department)
            # d.save()
            m_t = MeetingType.objects.create(meeting_type=type)
            m_t.save()
            m = Meeting.objects.create( theme=theme,
                                        department_id=department,
                                        time=time,
                                        place=place,
                                        sponsor_id=sponsor,
                                        meeting_type_id=m_t.meeting_type_id,
                                        state_id=stateid,
                                        content=content ,
                                        )
            #u = UserInfo.objects.create(id = userid,department_id=d.id)
            #u.save()

            mu_start = MeetingUserRelation.objects.count()

            #mu = MeetingUserRelation.objects.create( meeting_id=m.id,user_id=userid)#添加单个数据，不能添加数组（列表）数据

            l = len(userid)
            for x in range(l):
                 if userid[x]:

                     mu = MeetingUserRelation.objects.create(meeting_id=m.id,user_id=userid[x])
                     mu.save()
                 else:
                     break
            #mu.save()
            mu_end = MeetingUserRelation.objects.count()

            response = {}
            if mu_start <mu_end:

                response['message'] = '添加成功'
                response['flag'] = 'true'
                response['code'] = 20000
                data = {'is_succeed':1
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
            current_page_size = request.POST.get('pagesize')
            userid = request.POST.get('user_id')

            m = Meeting.objects.filter(meetinguserrelation__user_id=userid).values('meetinguserrelation__meeting_id','theme').distinct()
            paginator = Paginator(m,current_page_size)
            total = paginator.count
            page_x = paginator.page(number=current_page_num).object_list# current_page_num

            if m.exists():
              response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "total": total,
                    "data": list(page_x)#(page_x.object_list)
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
            #current_page_num = request.POST.get('page')
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

            #current_page_num = request.POST.get('page')
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
                data = {'is_succeed':1
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

            #current_page_num = request.POST.get('page')
            userid = request.POST.get('user_id')
            answerid = request.POST.get('answer_id')
            meetingid = request.POST.get('meeting_id')
            reason = request.POST.get('reason')

            m_u = MeetingUserRelation.objects.filter(user_id=userid,meeting_id=meetingid,answer_id=None,reason=None)
            #m_u.update()更新应该在判断之后
            # m = Meeting.objects.filter(meetinguserrelation__user_id=userid[0].id,place=place,id=meetingid,time__gte=time)

            response = {}
            if m_u.exists() :
                if answerid==1 :

                    m_u.update(answer_id=answerid,reason=reason)
                else:
                    m_u.update(answer_id=answerid)
                response['message'] = '应答成功'
                response['flag'] = 'true'
                response['code'] = 20000
                data = {'is_succeed':1
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


#5--10 会议类型查询接口
def ManagamentTypeDoApi(request):#ManagamentTypeDoApi
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
            current_page_size = request.POST.get('pagesize')
            m_t = MeetingType.objects.values('meeting_type_id','meeting_type')

            paginator = Paginator(m_t,current_page_size)
            total = paginator.count
            page_x = paginator.page(number=current_page_num).object_list# current_page_num

            if m_t.exists():
              response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "total": total,
                    "data": list(page_x)#(page_x.object_list)
                }
            else:
                response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "data": {}
                }

            return HttpResponse(json.dumps(response,cls=CJsonEncoder), content_type="application/json")

        else:
            return HttpResponse(json.dumps({"code":code,"message":"请登录"}), content_type="application/json")

    else:
        return HttpResponse("请用post方式访问")




#5--11、被邀请会议列表查询接口
def ManagamentInvitedDoApi(request):#ManagamentInvitedDoApi
    # [
    #     "meeting_id ": "1",
    # "theme": "XXXXX",
    # "department": "信息",
    # "time": "2020-5-31",
    # "place": "信息学院A307",
    # "sponsor": "李四",
    # "type": "XXXX",
    # "state": "未完成",
    # “answer”:{“参加”, ”请假”}
    # ]
    #

    if request.method == "POST":
        token = request.POST.get('token')
        code = request.POST.get('code')
        if check_token(token):
            current_page_num = request.POST.get('page')
            current_page_size = request.POST.get('pagesize')
            userid = request.POST.get('user_id')

            m = Meeting.objects.filter(meetinguserrelation__user_id=userid).values('id',
                                                                                   'theme',
                                                                                   'department__name',
                                                                                   'time',
                                                                                   'place',
                                                                                   'sponsor__user_name',
                                                                                   'meeting_type__meeting_type',
                                                                                   'state_id',#0为未开始，1为已结束
                                                                                   'meetinguserrelation__answer__answer',).order_by('id').distinct()

            paginator = Paginator(m,current_page_size)
            total = paginator.count
            page_x = paginator.page(number=current_page_num).object_list# current_page_num
            response = {}

            if m.exists():
              response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "total": total,
                    "data": list(page_x)#(page_x.object_list)
                }
            else:
                response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "data": {}
                }

            return HttpResponse(json.dumps(response,cls=CJsonEncoder), content_type="application/json")

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
            current_page_size = request.POST.get('pagesize')
            u = UserInfo.objects.values('id','user_name','department_id','department__name').order_by('id').distinct()
            paginator = Paginator(u,current_page_size)
            total = paginator.count
            page_x = paginator.page(number=current_page_num).object_list# current_page_num

            if u.exists():
              response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                     "total": total,
                    "data": list(page_x)#(page_x.object_list)
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
            current_page_size = request.POST.get('pagesize')
            d = Department.objects.values('id','name').order_by('id').distinct()
            paginator = Paginator(d,current_page_size)
            total = paginator.count
            page_x = paginator.page(number=current_page_num).object_list# current_page_num

            if d.exists():
              response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "total": total,
                    "data": list(page_x)#(page_x.object_list)
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



