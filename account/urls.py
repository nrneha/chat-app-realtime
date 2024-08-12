from django.urls import path

from account import views

urlpatterns = [
    path('',views.home_page,name="home"),
    path('login/',views.login_page,name="login"),
    path('signup/',views.signup_page,name="signup"),
    path('signup_stage/',views.signup_stage,name="signup_stage"),
    path('logout/',views.user_logout,name="logout"),
    path('user_login/',views.user_login,name="user_login"),
    path('view_account/<int:user_id>',views.view_account,name="view_account"),
    path('edit_account/<int:user_id>',views.edit_account,name="edit_account"),
    path('save_profile_updates/<int:user_id>',views.save_profile_updates,name="save_profile_updates"),


]



