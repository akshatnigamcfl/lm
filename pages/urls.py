from django.urls import path
# from .views import *
from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt import views as jwt_views
from django.conf import settings
from django.conf.urls.static import static
# from leads.views import *
from django.conf import settings
from django.conf.urls.static import static
from account.func import roleCheck
from pages.views import *


urlpatterns = [
    
    path('login', loginFun, name='user_login'),
    path('logout', logoutFun, name='user_logout'),
    path('my-info', my_infoFun, name='my_info'),
    
    path('', dashboardFun, name='dashboard'),
    path('dashboard', dashboardFun, name='dashboard'),
    path('users', usersFun, name='users'),
    path('leads', leadsFun, name='leads'),
    path('services', servicesFun, name='services'),
    path('approval', approvalsFun, name='approvals'),
    path('payments', paymentsFun, name='payments'),



# actions
    path('create_user_account', createUserAccountFun, name='create_user_account'),
    path('update_user_account', updateUserAccountFun, name='update_user_account'),
    path('archive_user', archiveUserFun, name='archive_user'),
    path('restore_user', restoreUserFun, name='restore_user'),


    path('hard_reset', hardReset, name='hard_reset'),
    path('custom_upload', customUpload, name='custom_upload'),
]



