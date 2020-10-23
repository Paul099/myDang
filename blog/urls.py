from django.conf.urls import url
from django.urls import path
from django.views.static import serve

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

    path('webname/taskprogress.do', views.TaskProgressApi),
    path('webname/tasktype.do', views.TaskTypeApi),
    path('webname/taskpriority.do', views.TaskPriorityApi),
    path('webname/taskstate.do', views.TaskStateApi),
    path('webname/tasksource.do', views.TaskSourceApi),

    path('webname/taskprogrecord.do', views.TaskProgRecordApi),

    path('webname/imguploadapi.do', views.ImgUploadApi),

    path('webname/getuser', views.GetUser),
    path('webname/taskanalysis', views.TaskAnalysisApi),


    url(r'^download/(?P<path>.*)$', serve, {'document_root':'/home/ubuntu/myDang/blog/download'})


]
