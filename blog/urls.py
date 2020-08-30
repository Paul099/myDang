from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginApi),
    path('index.do/', views.IndexDoApi),
    path('webname/index_most.do', views.MostDoApi),
    path('webname/list.do', views.ListDoApi),
    path('webname/index_work.do', views.WorkDoApi),


    path('webname/task.do', views.TaskDoApi),
    path('webname/taskget.do', views.TaskgetDoApi),
    path('webname/taskto.do', views.TaskToDoApi),
    path('webname/tasklist.do', views.TaskListDoApi),
    path('webname/taskadd.do', views.TaskAddDoApi),
    path('webname/taskson.do', views.TaskSonDoApi),
    path('webname/taskinquiry.do', views.TaskinQuiryDoApi),
    path('webname/taskmost.do', views.TaskMostDoApi),
    path('webname/taskurge.do', views.TaskUrgeDoApi),
    path('webname/taskstatistics.do', views.TaskStatisticsDoApi),
    path('webname/taskfor.do', views.TaskForDoApi),
    path('webname/taskfortion.do', views.TaskFortionDoApi),


]
