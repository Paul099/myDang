from django.urls import path
from . import views

urlpatterns = [
    #3.任务管理
    path('webname/Responslibity.do',views.ResponslibityDoApi),
    path('webname/Responslibitylist_sc.do',views.ResponslibitylistscDoApi),
    path('webname/Responslibity_list.do',views.ResponsLibitylistDoApi),
    #5.会议管理
    path('webname/managament.do',views.ManagamentDoApi),
    path('webname/managament_inquire.do',views.ManagamentInquireDoApi),
    path('webname/managament_specific.do', views.ManagamentSpecificDoApi),
    path('webname/managament_add.do', views.ManagamentAddDoApi),
    #path('webname/managament_invite.do', views.ManagamentInviteDoApi),
    path('webname/managament_query.do', views.ManagamentQueryDoApi),
    path('webname/managament_showto.do', views.ManagamentShowtoDoApi),
    path('webname/managament_showin.do',views.ManagamentShowinDoApi),
    path('webname/managament_answer.do',views.ManagamentAnswerDoApi),
    path('webname/managament_type.do',views.ManagamentTypeDoApi),
    #6.新增查询接口
    path('webname/user_inquire.do',views.UserInquireDoApi),
    path('webname/department_inquire.do',views.DepartmentInquireDoApi),





]
