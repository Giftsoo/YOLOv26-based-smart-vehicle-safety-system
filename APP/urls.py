from django.urls import path
from . import views

urlpatterns =[
    
    path('', views.Landing_1, name='Landing_1'),
    path('Register_2/', views.Register_2, name='Register_2'),
    path('Login_3/', views.Login_3, name='Login_3'),
    path('profile1/', views.profile, name='users-profile'),
    path('profile_list/',views.profile_list,name='profile_list'), 
    path('Home_4', views.Home_4, name='Home_4'),
    path('Teamates_5/', views.Teamates_5, name='Teamates_5'),
    path('Domain_Result_6/', views.Domain_Result_6, name='Domain_Result_6'),
    path('Problem_Statement_7/', views.Problem_Statement_7, name='Problem_Statement_7'),
    path('Per_Info_8/', views.Per_Info_8, name='Per_Info_8'),
    path('Deploy_9/', views.Deploy_9, name='Deploy_9'),
    path('Per_Database_10/', views.Per_Database_10, name='Per_Database_10'),
    path('Deploy_8/', views.Deploy_8, name='Deploy_8'),
    path('Per_Database_8/', views.Per_Database_8, name='Per_Database_8'),
    path('Logout/', views.Logout, name='Logout'),
    path('rear-video-feed/', views.rear_video_feed, name='rear_video_feed'),
    path("pothole-video-feed/", views.pothole_video_feed, name="pothole_video_feed"),
    path("stop-camera/", views.stop_camera, name="stop_camera"),
    path("alert-status/", views.alert_status, name="alert_status"),
]
