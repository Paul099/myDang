from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginApi),
    path('index.do/', views.IndexDoApi),
    path('webname/index_most.do', views.MostDoApi),

    path('webname/list.do', views.ListDoApi),
    path('webname/index_work.do', views.WorkDoApi),

]
