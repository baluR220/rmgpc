from django.urls import path
from rmgpc.core import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('home/execute_man/', views.execute_man, name='execute_man'),
    path('home/delete_man/', views.delete_man, name='delete_man'),
    path('home/delete_auto/', views.delete_auto, name='delete_auto'),
    path('home/new_manual/', views.new_manual, name='new_manual'),
    path('home/new_auto/', views.new_auto, name='new_auto'),
    path('mode/', views.mode, name='mode'),
    path('mode/save/', views.mode_save, name='mode_save'),
    path('sequence/', views.sequence, name='sequence'),
    path('sequence/new/', views.new_seq, name='new_seq'),
    path('sequence/delete/', views.delete_seq, name='delete_seq'),
    path('login/', views.MyLogin.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('settings/', views.settings_page, name='settings_page'),
    path('settings/new/', views.settings_new, name='settings_new'),
    path('get_man_status/', views.get_man_status, name='get_man_status'),
]
