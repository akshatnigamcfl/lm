from django.contrib import admin
from django.urls import path, include
from .views import *


urlpatterns = [

    # login & register
    path('login',Login.as_view(), name="login"),
    path('register',Register.as_view(),  name="register"),

    # user action
    path('user_list/<str:attribute>', GetUsersList.as_view(),  name="user_list"),
    path('users/<int:page>',Users.as_view()),
    path('user_search/<str:attribute>/<str:id>',UserSearch.as_view(), name="user_search"),
    path('user_update/<str:id>',UserUpdate.as_view(), name='user_update'),


    # employee leaves
    path('leave_action/<str:type>/<int:leave_id>',LeaveAction.as_view(), name="leave_action"),
    

    # path('user_delete/<str:employee_id>',delete_user.as_view()),
    # path('view_user_archive/<int:page>',view_users_archive.as_view()),
    # path('view_user_archive_search/<str:searchAtr>/<str:id>',view_users_archive_search.as_view()),
    # path('unarchive_user/<str:employee_id>',unarchive_user.as_view()),
    # path('my_info',my_info.as_view()),
    # path('apply_for_leave',apply_for_leave.as_view(), name="apply_for_leave"),
    # path('view_leave',view_leave.as_view()),
    # path('edit_leave/<int:leave_id>',edit_leave.as_view(), name="edit_leave"),
    # path('cancel_leave/<int:leave_id>',cancel_leave.as_view(), name="cancel_leave"),
    # path('view_all_leaves/<int:page>',view_all_leaves.as_view()),
    # path('approve_leave/<int:leave_id>',approve_leave.as_view(), name="approve_leave"),
    # path('reject_leave/<int:leave_id>',reject_leave.as_view(), name="reject_leave"),
    path('reset_first_login/<int:user_id>',ResetFirstLogin.as_view(), name="reset_first_login"),


    path('generate_password/<int:id>/<str:token>', GeneratePassword),

    # reset password
    path('reset_password', resetPassword, name="reset_password"),




    # path('approve_leave/<int:leave_id>',views.approve_leave.as_view(), name="approve_leave"),
    # path('reject_leave/<int:leave_id>',views.reject_leave.as_view(), name="reject_leave"),

    # extras
    # path('register',registration),
    # path('user_links',userSpecificLinkHeader.as_view()),
    # path('view_user_individual/<str:employee_id>',view_users_individual.as_view()),

]