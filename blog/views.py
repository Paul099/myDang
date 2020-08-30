from decimal import *
from blog.token_module import *
from django.db.models import Max
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
                response['message'] = '用户或密码不正确'
                response['flag'] = 'flase'
                response['code'] = 40000
                data = {}
            else:
                response['message'] = '登录正确'
                response['flag'] = 'true'
                response['code'] = 20000
                data = {'department_id': u[0].department_id, 'user_id': u[0].id, 'token': create_token(username)}
        else:
            response['message'] = '用户名不存在'
            response['flag'] = 'flase'
            response['code'] = 40000
            data = {}

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
        token = request.POST.get('token')
        if check_token(token):
            u = FileInfo.objects.filter(file_type=1).values()
            response = {}

            response['message'] = '查询成功'
            response['flag'] = 'true'
            response['code'] = 20000

            response['data'] = list(u)

            return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
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
        token = request.POST.get('token')
        if check_token(token):
            id = request.POST.get('id')
            code = request.POST.get('code')
            u = FileInfo.objects.filter(id=id, file_type=1)
            response = {}
            if u.exists():

                response['message'] = '查询成功'
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
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
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
        token = request.POST.get('token')
        if check_token(token):
            u = FileInfo.objects.filter(file_type=1).values()
            response = {}

            response['message'] = '查询成功'
            response['flag'] = 'true'
            response['code'] = 20000

            response['data'] = list(u)

            return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
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
        token = request.POST.get('token')
        if check_token(token):
            id = request.POST.get('id')
            code = request.POST.get('code')
            u = FileInfo.objects.filter(id=id, file_type=2)
            response = {}
            if u.exists():

                response['message'] = '查询成功'
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
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")


    else:

        return HttpResponse("请用post方式访问")


# ---------第四部分----------


def TaskDoApi(request):
    # {
    #     "code":"20000"
    #     "flag":"true"
    #     "message":"查询成功"
    #     "data":{
    #         "ls_task_num": "18",
    #         "ywc_task_num": "15",
    #         "wwc_task_num": "3",
    #         "by_task_num": "9",
    #         "cb_task_num": "2",
    #         "zp_task_num": "5"
    #     }
    # }

    if request.method == "POST":

        user_id = request.POST.get('user_id')
        code = request.POST.get('code')
        token = request.POST.get('token')
        if check_token(token):
            u_obj = TaskUserRelation.objects.filter(user=user_id)
            if u_obj.exists():
                ls_task_num = TaskUserRelation.objects.filter(user=user_id).count()
                # 落实任务总条数是参与数？
                ywc_task_num = Task.objects.filter(state=1, taskuserrelation__user_id=user_id).count()
                wwc_task_num = Task.objects.filter(state=2, taskuserrelation__user_id=user_id).count()
                by_task_num = TaskMessRecord.objects.filter(type=1, task__taskuserrelation__user_id=user_id).count()
                cb_task_num = TaskMessRecord.objects.filter(type=0, task__taskuserrelation__user_id=user_id).count()
                zp_task_num = Task.objects.filter(appointor=user_id).count()
                response = {
                    "code": "20000",
                    "flag": "true",
                    "message": "查询成功",
                    "data": {
                        "ls_task_num": ls_task_num,
                        "ywc_task_num": ywc_task_num,
                        "wwc_task_num": wwc_task_num,
                        "by_task_num": by_task_num,
                        "cb_task_num": cb_task_num,
                        "zp_task_num": zp_task_num
                    }
                }
            else:
                response = {
                    "code": "40000",
                    "flag": "false",
                    "message": "用户不存在",
                    "data": {

                    }

                }
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskgetDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "task_id ": "1",
    #     "task_title": "XXXXX",
    #     "cb_user": "3",
    #     "cb_time": "2020-5-31"
    # }
    # }
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        code = request.POST.get('code')
        token = request.POST.get('token')
        if check_token(token):
            u_set = Task.objects.filter(taskuserrelation__id=user_id).values('id', 'appointor__user_name', 'start_time',
                                                                             'title')

            response = {
                "code": "20000",
                "flag": "true",
                "message": "查询成功",
                "data": list(u_set)
            }

            return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskToDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "task_id ": "1",
    #     "task_title": "XXXXXX",
    #     "zs_user": "6",
    #     "time": "2019-5-31",
    #     "state": "未完成"
    # }
    # }
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        code = request.POST.get('code')
        token = request.POST.get('token')
        if check_token(token):

            u_set = TaskMessRecord.objects.filter(noti_user=user_id).values('task', 'task__title', 'noti_user__user_name',
                                                                        'time')
            response = {
                "code": "20000",
                "flag": "true",
                "message": "查询成功",
                "data": list(u_set)
            }
            return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskListDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "name": "XXXX",
    #     "role": "信息学院党支部书记",
    #     "task_num": "17",
    #     "ywc_task_num": "15",
    #     "wwc_task_num": "3",
    #     "cy_task_num": "2",
    #     "zp_task_num": "5"
    # 这都是啥啊
    # }
    # }
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        code = request.POST.get('code')
        token = request.POST.get('token')
        if check_token(token):
            name = UserInfo.objects.filter(id=user_id).values('user_name')
            role = RoleInfo.objects.filter(roleuserrelation__user_id=user_id).values()

            ywc_task_num = Task.objects.filter(state=1, taskuserrelation__user_id=user_id).count()
            wwc_task_num = Task.objects.filter(state=2, taskuserrelation__user_id=user_id).count()
            cy_task_num = TaskUserRelation.objects.filter(user=user_id).count()
            zp_task_num = Task.objects.filter(appointor=user_id).count()
            task_num = cy_task_num + zp_task_num
            response = {
                "code": "20000",
                "flag": "true",
                "message": "查询成功",
                "data": {
                    "name": name[0],
                    "role": role[0],
                    "task_num": task_num,
                    "ywc_task_num": ywc_task_num,
                    "wwc_task_num": wwc_task_num,
                    "cy_task_num": cy_task_num,
                    "zp_task_num": zp_task_num
                }
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskAddDoApi(request):
    if request.method == "POST":
        code = request.POST.get('code')
        task_title = request.POST.get('task_title')
        last_time = int(request.POST.get('last_time'))
        pre_task_id = request.POST.get('pre_task_id')
        appointor_id = request.POST.get('appointor_id')
        type = request.POST.get('type')
        is_secret = request.POST.get('is_secret')
        department = request.POST.get('department')
        user_id = request.POST.get('user_id')
        priority = request.POST.get('priority')
        content = request.POST.get('content')
        token = request.POST.get('token')
        if check_token(token):
            start_time = datetime.datetime.now()
            # time = datetime.timedelta(days=last_time)
            end_time = datetime.datetime.now() + datetime.timedelta(days=last_time)
            t = TaskType.objects.get(id=type)
            p = TaskPriority.objects.get(id=priority)
            # 传什么？
            #这个地方需要协商参与者和完成人，还有全部的add是否对外键做处理？？？？？？？？？？
            #所属单位传id还是名称

            m_idmax = Task.objects.aggregate(idmax=Max('id'))
            u = Task(id=m_idmax['idmax'] + 1, title=task_title, end_time=end_time, start_time=start_time, pid=pre_task_id,
                     appointor=appointor_id,
                     type=t, department_id=department, priority=p, content=content)
            u.save()
            u2 = TaskUserRelation(user_id=user_id, task_id=u.id)
            u2.save()
            response = {
                "code": "20000",
                "flag": "true",
                "message": "保存成功",
                "data": {
                    "is_succeed": "1",
                    "task_id": u.id
                }
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskSonDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "is_succeed": "1",
    #     "task_id": "4"
    # }
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        task_title = request.POST.get('task_title')
        last_time = int(request.POST.get('last_time'))
        pre_task_id = request.POST.get('pre_task_id')  # 子任务不需要父节点？
        user_id = request.POST.get('priority_id')
        content = request.POST.get('content')
        token = request.POST.get('token')
        if check_token(token):
            start_time = datetime.datetime.now()
            end_time = datetime.datetime.now() + datetime.timedelta(days=last_time)
            m_idmax = Task.objects.aggregate(idmax=Max('id'))
            u = Task(id=m_idmax['idmax'] + 1, title=task_title, end_time=end_time, start_time=start_time, pid=pre_task_id,
                     content=content)
            u.save()
            u2 = TaskUserRelation(user_id=user_id, task_id=u.id)
            u2.save()
            response = {
                "code": "20000",
                "flag": "true",
                "message": "保存成功",
                "data": {
                    "is_succeed": "1",
                    "task_id": u.id
                }
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskinQuiryDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "task_id ": "6",
    #     "task_tilte": "XXXXX",
    #     "last_time": "24",
    #     "pre_task ": "XXXXXX",
    #     "appointor": "张三",
    #     "type": "XXXX",
    #     "progress": "50%",
    #     "department": "信息学院"
    # }
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        state = int(request.POST.get('state'))  # 1完成 2未完成 3参与 4指派
        user_id = request.POST.get('user_id')
        token = request.POST.get('token')
        if check_token(token):
            if state == 1:
                u_set = Task.objects.filter(state=1, taskuserrelation__user_id=user_id).values("id", "title", "start_time",
                                                                                               "end_time", "pid",
                                                                                               "appointor__user_name",
                                                                                               "type__type", "progress",
                                                                                               "department_id")
                # pid缺外键
                # 持续时间自己算
            elif state == 2:
                u_set = Task.objects.filter(state=2, taskuserrelation__user_id=user_id).values("id", "title", "start_time",
                                                                                               "end_time", "pid",
                                                                                               "appointor__user_name",
                                                                                               "type__type", "progress",
                                                                                               "department_id")
            elif state == 3:
                u_set = Task.objects.filter(taskuserrelation__user_id=user_id).values("id", "title", "start_time",
                                                                                      "end_time", "pid",
                                                                                      "appointor__user_name", "type__type",
                                                                                      "progress", "department_id")
            elif state == 4:
                u_set = Task.objects.filter(appointor=user_id).values("id", "title", "start_time", "end_time", "pid",
                                                                      "appointor__user_name", "type__type", "progress",
                                                                      "department_id")

            response = {
                "code": "20000",
                "flag": "true",
                "message": "查询成功",
                "data": list(u_set)
            }
            return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskMostDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "task_id ": "6",
    #     "task_tilte": "XXXXX",
    #     "last_time": "24",
    #     "pre_task ": "XXXXX",
    #     "appointor": "张三",
    #     "type": "XXXX",
    #     "progress": "50%",
    #     "department": "信息学院",
    #     "cy_user": "8",
    #     "priority": "50%",
    #     "content": "XXXXX",
    #     {
    #         "task_id": "6",
    #         "task_tilte": "XXXXXX",
    #         "user_id": "9",
    #         "progress": "50%"
    #     }
    #         "mess_type": "表扬",
    #                      "mess_time": "2020-6-28"
    # }
    # }

    if request.method == "POST":
        code = request.POST.get('code')
        task_id = request.POST.get('task_id')
        token = request.POST.get('token')
        if check_token(token):
            u_obj = Task.objects.filter(id=task_id).values("title", "start_time", "end_time", "pid",
                                                           "taskuserrelation__user__user_name", "type__type", "progress",
                                                           "department_id")
            data = u_obj[0]
            cy_user = TaskUserRelation.objects.filter(task_id=task_id).count()
            data["cy_user"] = cy_user
            u_set = Task.objects.filter(pid=task_id).values("id", "title", "start_time", "end_time", "pid",
                                                            "taskuserrelation__user", "progress",
                                                            )
            data["son"] = list(u_set)
            mess_set = TaskMessRecord.objects.filter(task_id=task_id).values("type", "time")
            # 这里的type是varchar很奇怪
            data["mess"] = list(mess_set)
            response = {
                "code": "20000",
                "flag": "true",
                "message": "查询成功",
                "data": data
            }

            return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskUrgeDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "is_succeed": "1"
    # }
    # }
    if request.method == "POST":
        code = request.POST.get('code')
        task_id = request.POST.get('task_id')

        oper_user_id = request.POST.get('user_id')
        mess_type_id = request.POST.get('mess_type_id')
        token = request.POST.get('token')
        if check_token(token):
            m_idmax = TaskMessRecord.objects.aggregate(idmax=Max('id'))

            noti_user_id=TaskUserRelation.objects.filter(task_id=task_id)[0].user_id
            u1 = UserInfo.objects.get(id=oper_user_id)
            u2 = UserInfo.objects.get(id=noti_user_id)
            u = TaskMessRecord(id=m_idmax['idmax'] + 1, type=mess_type_id, noti_user=u2, oper_user=u1,
                               task_id=task_id, time=datetime.datetime.now())
            # 为什么没有操作人
            u.save()
            response = {
                "code": "20000",
                "flag": "true",

                "data": {"is_succeed": "1"}
            }

            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskStatisticsDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "party_branch": "信息学院党支部",
    #     "par_task_num": "2",
    #     "department": "信息学院",
    #     "dep_task_num": "17"
    # }
    # }
    # department应该是缺表
    # role缺字段缺外键

    if request.method == "POST":
        code = request.POST.get('code')
        user_id = request.POST.get('user_id')
        token = request.POST.get('token')
        if check_token(token):
            p_obj=PartyUserRelation.objects.filter(user_id=user_id)
            d_obj = Task.objects.filter(taskuserrelation__user__partyuserrelation=user_id)
            #这样也可以  Task.objects.filter(taskuserrelation__user_id=1)[0].department.name
            response = {
                "code": "20000",
                "flag": "true",
                "message": "查询成功",
                "data": {
                    "party_branch": p_obj.values("party_branch__party_branch")[0]["party_branch__party_branch"],
                    "par_task_num": Task.objects.filter().count(),
                    "department": d_obj.values("department__name")[0]["department__name"],
                    "dep_task_num": d_obj.count()
                }
            }

            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskForDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "task_id ": "6",
    #     "task_tilte": "XXXXX",
    #     "last_time": "24",
    #     "pre_task ": "XXXX",
    #     "appointor": "张三",
    #     "type": "XXXX",
    #     "progress": "50%",
    #     "department": "信息学院"
    # }
    # }
    # 完成人appointor有争议

    if request.method == "POST":
        code = request.POST.get('code')
        department_id = request.POST.get('department_id')
        token = request.POST.get('token')
        if check_token(token):
            u_set = Task.objects.filter(department_id=department_id).values("id", "title", "start_time", "end_time",
                                                                            "source__source",
                                                                            "appointor__user_name", "progress",
                                                                            "department__name"
                                                                            )
            response = {
                "code": "20000",
                "flag": "true",
                "message": "查询成功",
                "data": list(u_set)
            }

            return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")


def TaskFortionDoApi(request):
    # {
    #     "code": "20000"
    #             "flag": "true"
    #                     "message":"查询成功"
    #                               "data": {
    #     "task_id ": "6",
    #     "task_tilte": "XXXXX",
    #     "last_time": "24",
    #     "pre_task ": "XXXXX",
    #     "appointor": "张三",
    #     "type": "XXXX",
    #     "progress": "50%",
    #     "department": "信息学院"
    # }
    # }

    if request.method == "POST":

        # Task.objects.filter().values("id", "title", "start_time", "end_time",
        #                                                         "source__source",
        #                                                         "appointor__user_name", "progress", "department_id"
        # 缺外键
        user_id = request.POST.get('user_id')
        token = request.POST.get('token')
        if check_token(token):
            d_set = Task.objects.filter(taskuserrelation__user__partyuserrelation=user_id).values("id","title","start_time","end_time","pid","appointor__user_name","type__type","progress","department__name")
            response = {
                "code": "20000",
                "flag": "true",
                "message": "查询成功",
                "data": list(d_set)
            }

            return HttpResponse(json.dumps(response, cls=CJsonEncoder), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"message":"请登录"}), content_type="application/json")
    else:

        return HttpResponse("请用post方式访问")
