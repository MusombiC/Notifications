from django.urls import include,path


from . import views

urlpatterns = [
    path('deepthought/', view= views.DeepThoughtView.as_view(), name='musombi_notifications_deepthought'), 
    path('fcm/', include('fcm.urls'))
]