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
    path('webname/managament_invite.do', views.ManagamentInviteDoApi),
    path('webname/managament_sign.do',views.ManagamentSignDoApi)




]
