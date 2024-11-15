from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('',include('pages.urls')),
   #  path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('account/',include('account.urls')),
    # path('core/',include('core.urls')),
    path('leads/',include('leads.urls')),
    

   #  path('login',loginpage),
    path('dropdown/',include('dropdown.urls')),
   #  path('employees/',include('employees.urls')),
    # path('evitamin/',include('evitamin.urls')),
   #  path('records/',include('records.urls')),
    # path('appointment/',include('appointment.urls')),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='verify_token'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
