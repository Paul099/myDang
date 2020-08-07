from django.urls import path
from . import views

urlpatterns = [

    path('webname/Responslibity.do',views.ResponslibityDoApi),
    path('webname/Responslibitylist_sc.do',views.ResponslibitylistscDoApi)


]
