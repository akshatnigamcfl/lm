from django.shortcuts import render
from .serializers import *
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from account.views import *
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from django.apps import apps



# Create your views here.


def resFun(status,message,data):
    res = Response()
    res.status_code = status
    res.data = {
        'status': status,
        'message': message,
        'data': data,
    }
    return res



class EmployeeList(GenericAPIView):
    serializer_class = CommonDropdownSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, attribute, format=None, *args, **kwargs):
        user = request.user
        try:
            if attribute == 'team_member':                
                searchData = UserAccount.objects.filter(reporting_manager = user.id, employee_status__title='active').distinct()
            else:
                searchData = UserAccount.objects.filter(user_role__title = attribute, visibility=True).distinct()
            
            return employeeListFun(searchData, attribute)
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST,'request failed',[e.detail])



def employeeListFun(searchData, attribute):
    if searchData==None:
        return resFun(status.HTTP_400_BAD_REQUEST,'search attribute not valid',[])
    elif searchData.exists():
        data =[]
        for d in searchData:
            if attribute == 'team_member':

                today = datetime.now().date()
                employee_leave_instance = EmployeeLeaves.objects.filter(employee=d.id, status__title='approved').filter(date_from__lte=today).filter(date_to__gte=today)
                # .filter(Q(date_from__lte=today) | Q(date_to__gte=today))
                # print('employee_leave_instance', employee_leave_instance )
                if employee_leave_instance.exists():
                    for em in employee_leave_instance:
                        # if not em.date_from <= today <= em.date_to:
                        data.append({'id': d.id, 'value': d.name})
                else:
                    data.append({'id': d.id, 'value': d.name})
            else:
                data.append({'id': d.id, 'value': d.name})
        serializer = CommonDropdownSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return resFun(status.HTTP_200_OK,'request successful',{'data': serializer.data, 'search_attribute': attribute})
    else:
        return resFun(status.HTTP_204_NO_CONTENT,'data not found',{'data': [], 'search_attribute': attribute})





class CommercialList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommonDropdownSerializer
    def get(self, request, lead_id, marketplace_id, program_id, format=None, *args, **kwargs):
        try:
            program = Program.objects.filter(marketplace__id=marketplace_id, id=program_id).first()
            if not program:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid program id', [])
            
            service_commercial_instance = Program.objects.filter(id = program_id)            
            
            if not service_commercial_instance:
                return resFun(status.HTTP_400_BAD_REQUEST, 'commercial not created', [])
            data = []
            for so in service_commercial_instance:
                for sc in so.commercials.all():
                    if not sc.lead_id.filter(lead_id = lead_id).exists():
                        data.append({'id': sc.id, 'value': sc.commercials })
            if lead_id != 'bulk':
                service_category_instance = ServiceCategory.objects.filter(lead_id=lead_id)
                for s in service_category_instance.first().program.commercials.all():
                    if s.lead_id.all().exists():
                        if s.lead_id.filter(id = service_category_instance.first().id).exists() and service_category_instance.first().commercial_approval !=None and service_category_instance.first().commercial_approval.status.title =='approved':
                            data.append({"id": s.id, "value": s.commercials})

            return resFun(status.HTTP_200_OK, 'request successful', data)
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
        


class DropdownOption(GenericAPIView):
    serializer_class = DropdownOptionSerializers
    permissions_classes = [IsAuthenticated]
    def get(self, request, table, format=None, *args, **kwargs):
        try:
            main_app = 'dropdown'
            print(main_app)
            if not(table == 'approvalstatus' or table == 'notinterested' or table == 'unresponsive' or table == 'clientdesignation' ): 
                main_app = 'leads'

            model = apps.get_model(main_app, table)
            data = model.objects.all().order_by('title')
            main_data = [{"id": d.id, "title": d.title } for d in data]
            serializer = DropdownOptionSerializers(data=main_data, many=True)
            serializer.is_valid(raise_exception=True)
            return resFun(status.HTTP_200_OK, 'successful', {'data': serializer.data, 'table_name': table})
            
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [e.detail])



class LeadStatusList(GenericAPIView):
    permissions_classes = [IsAuthenticated]
    serializer_class = DropdownOptionSerializers
    def get(self, request, format=None, *args, **kwargs):
        try:
            lead_status = LeadStatus.objects.all().order_by('title').values()
            serializer = DropdownOptionSerializers(data=list(lead_status), many=True)
            serializer.is_valid(raise_exception=True)
            res =  resFun(status.HTTP_200_OK, 'successful', serializer.data)
            return res
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])
        


class Commercials(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommonDropdownSerializer
    def get(self, request, client_id, lead_id, format=None, *args, **kwargs):
        try:
            lead_instance = Leads.objects.get(client_id=client_id, visibility=True)
            service_category_instance = lead_instance.service_category.filter(lead_id=lead_id)

            if service_category_instance.exists():
                data=[{"id": l.id, "value": l.commercials} for l in service_category_instance.first().program.commercials.all() if not len(l.lead_id.all())>0 ]

                for s in service_category_instance.first().program.commercials.all():   
                    if s.lead_id.all().exists():
                        if s.lead_id.filter(id = service_category_instance.first().id).exists() and service_category_instance.first().commercial_approval !=None and service_category_instance.first().commercial_approval.status.title =='approved':
                            data.append({"id": s.id, "value": s.commercials})

                data.append({"id": 0, "value": 'others'})
                if len(data) > 0: 
                    serializer =  CommonDropdownSerializer(data=data, many=True)
                    serializer.is_valid(raise_exception=True)
                    return  resFun(status.HTTP_200_OK, 'request successful', serializer.data)
                else:
                    return  resFun(status.HTTP_204_NO_CONTENT, 'no data found, contact super admin to create commercials for this service', [])
            else:
                return  resFun(status.HTTP_204_NO_CONTENT, 'no data', [])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [e.detail])
