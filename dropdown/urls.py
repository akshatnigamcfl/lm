from django.urls import path
from .views import *

urlpatterns = [

    # Employee
    path('employee_list/<str:attribute>', EmployeeList.as_view(), name='employee_list'),

    # Leads
    path('lead_status_list', LeadStatusList.as_view(), name="lead_status_list"),
    

    # commercials
    path('commercials/<str:client_id>/<str:lead_id>', Commercials.as_view(), name='commercials'),
    path('commercial_list/<str:lead_id>/<str:marketplace_id>/<str:program_id>', CommercialList.as_view(), name='commercial_list'),
    path('options/<str:table>', DropdownOption.as_view(), name='options'),


    
]
