from django.shortcuts import render
from leads.models import *
from account.models import *
from leads.serializers import *
from leads.serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView,CreateAPIView
from rest_framework.permissions import IsAuthenticated
from account.views import roleCheck
from rest_framework.exceptions import ValidationError
from django.forms.models import model_to_dict
from account.func import SendEmail, getClientId, getLeadId
from django.core.mail import EmailMultiAlternatives
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
import math
from django.db.models import Q
from datetime import date, datetime, timezone, timedelta
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.http import FileResponse
from django.apps import apps
from django.db.models import OuterRef, Subquery
from account.views import IgnoreBearerTokenAuthentication















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


class CreateLeadUpload(CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = LeadUploadSerializer
    def post(self, request, format=None, *args, **kwargs):
        user = request.user
        
        if roleCheck(user,'super_admin') or roleCheck(user,'admin') or request.user.is_admin :
            if request.method == 'POST':
                if request.FILES:
                    file = request.FILES['file']
                    df = pd.read_csv(file, delimiter=',',   header=0)
                    df = pd.DataFrame(df)
                    df = df.astype(object)
                    df.fillna('', inplace=True)
                    head_row = df.columns.values
                    h_row = [f.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('__', '_').replace('__', '_').lower() for f in head_row]
                    h_row[h_row.index('requester_name')] = 'client_name'
                    h_row[h_row.index('phone_number')] = 'contact_number'
                    # h_row[h_row.index('service_category')] = 'service_category'

                    db_head_row_all_rw = Leads._meta.get_fields()
                    db_head_row_all = [field.name for field in db_head_row_all_rw]

                    # db_head_row_all_type = [field.get_internal_type() for field in db_head_row_all_rw]

                    # db_head_row_phNum_rw = Contact_number._meta.get_fields()
                    # db_head_row_phNum = [field.name for field in db_head_row_phNum_rw]

                    # db_head_row_emlId_rw = email_ids._meta.get_fields()
                    # db_head_row_emlId = [field.name for field in db_head_row_emlId_rw]

                    list_of_csv = [list(row) for row in df.values]
                    output_data = []

                    ref_id = ''

                    for ls in list_of_csv:
                        dup = False
                        break_out = True
                        dup_data = None

                        ind_contact_number = h_row.index('contact_number')
                        ind_email_id = h_row.index('email_id')

                        dup_contact = str(math.trunc(int(ls[ind_contact_number])) if ls[ind_contact_number] != '' else '')
                        dup_email = str(ls[ind_email_id] if ls[ind_email_id] != '' else '')

                        

                        dup_contact_number = Leads.objects.filter(Q(contact_number__icontains = dup_contact) | Q(alternate_contact_number__icontains = dup_contact))
                        duplicate_contacts = []
                        if dup_contact_number.exists():
                            for d in dup_contact_number:

                                [{ 'lead_id': r.lead_id, 'remarks': [ rm.remark for rm in  r.remark.all()]} for r in d.service_category.all()]
                                
                                duplicate_contacts.append({
                                    'client_id': str(d.client_id), 
                                    'data': [{ 'lead_id': r.lead_id, 'remarks': [ rm.remark for rm in  r.remark.all()]} for r in d.service_category.all()] 
                                    })

                        dup_email_id = Leads.objects.filter(Q(email_id = dup_email) | Q(alternate_email_id = dup_email))
                        duplicate_email = []
                        if dup_email_id:
                            for d in dup_email_id:
                                if len(duplicate_contacts) > 0:
                                    for dt in duplicate_contacts:
                                        if dt['client_id'] == d.client_id:
                                            break
                                else:
                                    duplicate_email.append({
                                        'client_id': str(d.client_id), 
                                        'data': [{ 'lead_id': r.lead_id, 'remarks': [ rm.remark for rm in  r.remark.all()]} for r in d.service_category.all()] 
                                        })
                                    
                        if len(duplicate_contacts) > 0 or len(duplicate_email) > 0:
                            dup = True
                            break_out = False
                            error_message = ['already exists']
                            dup_data =  duplicate_contacts + duplicate_email

                        if dup == False:
                            dt = {}
                            client_id = getClientId()
                            leads_instance = Leads()

                            


                            for i in range (len(db_head_row_all)):
                                if not (db_head_row_all[i] == 'id' or db_head_row_all[i] == 'Client_id') and db_head_row_all[i] in h_row:
                                    ind = h_row.index(db_head_row_all[i])

                                    # if db_head_row_all[i] == 'marketplace':
                                    #     dt[db_head_row_all[i]] = Services_and_Commercials.objects.filter(marketplace__marketplace = ls[ind].lower()).first()


                                    if db_head_row_all[i] == 'service_category':

                                        if ls[h_row.index('service_category')] == '':
                                            break_out = False
                                            error_message = ['service category can not be blank']
                                            break
                                        elif ls[h_row.index('marketplace')] == '':
                                            break_out = False
                                            error_message = ['marketplace can not be blank']
                                            break
                                        elif ls[h_row.index('program')] == '':
                                            break_out = False
                                            error_message = ['program can not be blank']
                                            break
                                        else:


                                            program = Program.objects.filter(
                                                program = ls[h_row.index('program')].lower(),
                                                marketplace__marketplace = ls[h_row.index('marketplace')].lower(),
                                                marketplace__service__service = ls[ind].lower(),
                                                marketplace__service__segment__segment = ls[h_row.index('segment')].lower(),
                                            )


                                            print('program', program)

                                            if not program.exists():
                                                break_out=False
                                                error_message = ['service & commercials not found']
                                                break


                                    elif db_head_row_all[i] == 'request_id':
                                        if ls[ind] != '':
                                            if len(str(ls[ind])) > 0:
                                                dt[db_head_row_all[i]] = ls[ind]
                                        else:
                                            break_out = False
                                            error_message = ['request id can not be blank']
                                            break

                                    elif db_head_row_all[i] == 'status':
                                        dt[db_head_row_all[i]] = 'yet_to_contact'

                                    elif db_head_row_all[i] == 'contact_number':
                                        dup_contact = str(math.trunc(int(ls[ind_contact_number])) if ls[ind_contact_number] != '' else '')
                                        dt[db_head_row_all[i]] = dup_contact


                                    else:
                                        if isinstance(ls[ind], str):
                                               dt[db_head_row_all[i]] = ls[ind].lower()
                                        elif isinstance(ls[ind], float):
                                            if ls[ind] != '':
                                                dt[db_head_row_all[i]] = str(ls[ind])
                                            else:
                                                dt[db_head_row_all[i]] = ''
                                        elif isinstance(ls[ind], int):
                                            if ls[ind] != '':
                                                dt[db_head_row_all[i]] = str(ls[ind])
                                            else:
                                                dt[db_head_row_all[i]] = ''
                                        else: 
                                            dt[db_head_row_all[i]] = ls[ind]

                        if break_out:
                            # Status_history.objects.create({'service'})
                            d = [client_id]
                            head_rows = [h for h in h_row]
                            head_rows.insert(0, 'client_id')
                            d = d + ls
                            # head_rows.insert(0, 'status')
                            # d = [str(drp_lead_status.objects.filter(title = 'yet to contact').first().title)] + d
                            output_data.append(dict(zip(head_rows ,d)))

                            dt['client_id'] = str(client_id)
                            # dt['status'] = drp_lead_status.objects.filter(title = 'yet to contact').first()
                            dt['lead_owner'] = request.user

                            service_category_instance = ServiceCategory.objects.create(**{
                                'lead_id': getLeadId() ,
                                # 'program':  Program.objects.filter(marketplace ) ,
                                'program':program.first()
                                })
                            
                            
                            Status_history_instance = StatusHistory.objects.create(**{
                                'status': LeadStatus.objects.filter(title = 'yet_to_contact').first(), 
                                'status_date': date.today() ,
                                'updated_by': request.user, 
                                'service_category': service_category_instance 
                                })
                            
                            def getHistoryInstance(title):
                                lead_history_instance = LeadHistory.objects.create(**{
                                    "action_type" : ActionType.objects.filter(title = 'created').first(),
                                    "title": title,
                                    "updated_by" : request.user,
                                    })
                                return lead_history_instance
                            
                            for field_name, value in dt.items():
                                if field_name != 'city':
                                    setattr(leads_instance, field_name, value)
                            leads_instance.save()

                            leads_instance.history.add(getHistoryInstance('lead created'))
                            service_category_instance.history.add(getHistoryInstance('service created'))
                            service_category_instance.status_history.add(Status_history_instance)
                            leads_instance.service_category.add(service_category_instance.id)

                        else:
                            d = ['not generated']
                            head_rows = [h for h in h_row]
                            if dup_data:
                                head_rows.insert(0, 'duplicate_leads')
                                data = [dup_data] + ls
                            else:
                                data = ls
                            head_rows.insert(0, 'client_id')
                            d = d + data
                            head_rows.insert(0, 'error_message')
                            d = error_message + d
                            
                            output_data.append(dict(zip(head_rows ,d)))

                    # res['Access-Control-Allow-Origin'] = '*'
                    # res['Access-Control-Allow-Credentials'] = True
                    return resFun(status.HTTP_200_OK, "all records saved successfully", output_data )
                else :
                    return resFun(status.HTTP_400_BAD_REQUEST, "file object not provided with key 'file'", [] )
            else:        
                return resFun(status.HTTP_400_BAD_REQUEST, "unsuccessful", [] )
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, "you are not authorized for this action", [] )


class CreateLeadManual(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateLeadManualSerializer
    def post(self, request, format=None, *args, **kwargs):
        try:
            serializer = CreateLeadManualSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                if serializer.save():
                    serializer.instance.lead_owner = request.user
                    for s in serializer.validated_data['program']:
                        program = Program.objects.filter(id=s)

                        def getHistoryInstance(title):
                            lead_history_instance = LeadHistory.objects.create(**{"action_type" : ActionType.objects.filter(title = 'created').first(),"title": title,"updated_by" : request.user,})
                            return lead_history_instance
                        
                        serializer.instance.history.add(getHistoryInstance('lead created'))
                        service_instance = ServiceCategory.objects.create(**{'lead_id': getLeadId(),'program': program.first() })
                        service_instance.history.add(getHistoryInstance('service created'))
                        status_history = StatusHistory.objects.create(**{'status': LeadStatus.objects.get(title='yet_to_contact'), 'updated_by': request.user, 'service_category': service_instance })

                        service_instance.status_history.add(status_history)
                        serializer.instance.service_category.add(service_instance)
                
                    res = resFun(status.HTTP_200_OK, 'lead registered successfully', [])
                    return res
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])



class UpdateLead(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateLeadSerializer
    def put(self, request, client_id, format=None, *args, **kwargs):
        try:
            try:
                lead_instance = Leads.objects.get(client_id=client_id)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid client id', [])

            data = model_to_dict(lead_instance)
            for fields in lead_instance._meta.many_to_many:
                print('fields', fields)
                related_objects = getattr(lead_instance, fields.name).all()
                data[fields.name] = [model_to_dict(obj) for obj in related_objects]
            
            service_category_instance=lead_instance.service_category.get(lead_id = request.data['lead_id'])
            lead_history_data = []
            old_values = model_to_dict(lead_instance)
            
            def updateHistory():
                for k,v in request.data.items():
                    if k == 'commercial_id' :
                        if service_category_instance.commercials == None:
                                lead_history_data.append( { 'key': k.replace('_id', ''), 'previous': '' , 'new': Commercials.objects.filter(id=int(request.data[k]) ).first().commercials })
                        else:
                            if model_to_dict(service_category_instance.commercials)['id'] != request.data[k]:
                                lead_history_data.append( { 'key': k.replace('_id', ''), 'previous': Commercials.objects.filter( id = int(model_to_dict(service_category_instance.commercials)['id']) ).first().commercials , 'new': Commercials.objects.filter(id=int(request.data[k]) ).first().commercials })
                    elif k != 'lead_id' :
                        if old_values[k] != request.data[k]:
                            if k == 'client_designation' :
                                    client_designation_instance = ClientDesignation.objects.filter( id = int(old_values[k]) ).first() if old_values[k] != None else ''
                                    lead_history_data.append({ 
                                        'key': k, 
                                        'previous': client_designation_instance.title if client_designation_instance else '',  
                                        'new': ClientDesignation.objects.filter( id = int(request.data[k]) ).first().title if ClientDesignation.objects.filter( id = int(request.data[k]) ).first() else '' })
                            elif k == 'client_turnover' :
                                    client_turnover_instance = ClientTurnover.objects.filter( id = int(old_values[k]) ).first() if old_values[k] != None else ''
                                    lead_history_data.append( {
                                        'key': k,
                                        'previous': client_turnover_instance.title if client_turnover_instance else '', 
                                        'new': ClientTurnover.objects.filter(id=int(request.data[k]) ).first().title if ClientTurnover.objects.filter(id=int(request.data[k]) ).first() else '' })
                            elif k == 'business_category' :
                                    business_category_instance = BusinessCategory.objects.filter( id = int(old_values[k]) ).first() if old_values[k] != None else ''
                                    lead_history_data.append({ 
                                        'key': k, 
                                        'previous': business_category_instance,
                                        'new': BusinessCategory.objects.filter(id=int(request.data[k]) ).first().title if BusinessCategory.objects.filter(id=int(request.data[k]) ).first() else '' })
                            else:
                                if  old_values[k] != '' :
                                    lead_history_data.append( {'key': k,'previous': old_values[k], 'new': request.data[k] })
            updateHistory()

            serializer = UpdateLeadSerializer(lead_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            serializer.instance.history.add(LeadHistory.objects.create(action_type=ActionType.objects.filter(title='updated').first(), field = lead_history_data, title = 'lead updated', updated_by = request.user ))
            service_category_instance = serializer.instance.service_category.get(lead_id=serializer.validated_data['lead_id'])

            if serializer.validated_data.get('status'):
                service_category_instance.status = serializer.validated_data['status']
            if serializer.validated_data.get('commercial_id'):
                service_category_instance.commercials = serializer.validated_data['commercial_id']
            if roleCheck(request.user,'business_development_associate') and roleCheck(request.user,'business_development_team_lead'):
                if serializer.validated_data.get('associate'):
                    service_category_instance.associate = serializer.validated_data['associate']
            service_category_instance.save()
            return resFun(status.HTTP_200_OK, 'request successful', [])

        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [e.detail])

    


def commercialsWithPrograms(type, program_id):
    try:
        program = Program.objects.get(id=program_id)
    except:
        program = Program.objects.get(pk__in=[])
    
    if program:
        if type == 'active':
            commercials = [ {'id': p.id, 'value': p.commercials} for p in program.commercials.filter(visibility=True)]
        elif type == 'archive':
            commercials = [ {'id': p.id, 'value': p.commercials} for p in program.commercials.filter(visibility=False)]
        
        serializers = ServiceCreateActiveCommercialSerializer(data=commercials, many=True)
        if serializers.is_valid(raise_exception=True):
            res = resFun(status.HTTP_200_OK, 'request successful', serializers.data) 
        else:
            res = resFun(status.HTTP_200_OK, 'request failed', []) 
    else:
        res = resFun(status.HTTP_400_BAD_REQUEST, 'data not found', [])
    return res




class AllLeads(GenericAPIView):
    serializer_class = LeadsSerializer
    # permission_classes = [IsAuthenticated]
    authentication_classes = [IgnoreBearerTokenAuthentication]
    def get(self, request, limit, page, format=None, *args, **kwargs):
        user = request.user
        # limit = 10
        offset = int((page - 1) * limit)
        data = []
        pagecount = 1


        client_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_id')[:1])
        client_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_name')[:1])
        contact_number_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('contact_number')[:1])
        alternate_contact_number_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('alternate_contact_number')[:1])
        email_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('email_id')[:1])
        alternate_email_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('alternate_email_id')[:1])
        hot_lead_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('hot_lead')[:1])
        request_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('request_id')[:1])
        provider_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('provider_id')[:1])
        requester_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_id')[:1])
        requester_location_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_location')[:1])
        business_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_name')[:1])
        requester_sell_in_country_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_sell_in_country')[:1])
        gst_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('gst')[:1])
        service_requester_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('service_requester_type')[:1])
        upload_date_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('upload_date')[:1])
        business_category_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_category')[:1])
        client_turnover_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_turnover')[:1])
        brand_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('brand_name')[:1])
        seller_address_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('seller_address')[:1])
        lead_owner_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('lead_owner')[:1])
        contact_preferences_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('contact_preferences')[:1])
        firm_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('firm_type')[:1])
        business_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_type')[:1])
        client_designation_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_designation')[:1])
        # Subquery to get the latest status title for each Service_category
        latest_status_subquery = Subquery(StatusHistory.objects.filter(service_category=OuterRef('pk')).order_by('-id').values('status__title')[:1])
  

        leadsData = ServiceCategory.objects.annotate(
            client_id=client_id_subquery, 
            client_name=client_name_subquery, 
            contact_number=contact_number_subquery, 
            alternate_contact_number=alternate_contact_number_subquery, 
            email_id=email_subquery,
            alternate_email_id=alternate_email_subquery,
            hot_lead = hot_lead_subquery,
            request_id = request_id_subquery,
            provider_id = provider_id_subquery,
            requester_id = requester_id_subquery,
            requester_location = requester_location_subquery,
            business_name = business_name_subquery,
            requester_sell_in_country = requester_sell_in_country_subquery,
            gst = gst_subquery,
            service_requester_type = service_requester_type_subquery,
            upload_date = upload_date_subquery,
            business_category = business_category_subquery,
            client_turnover = client_turnover_subquery,
            lead_owner = lead_owner_subquery,
            brand_name = brand_name_subquery,
            seller_address = seller_address_subquery,

            contact_preferences = contact_preferences_subquery,
            firm_type = firm_type_subquery,
            business_type = business_type_subquery,
            client_designation = client_designation_subquery,

            last_status_title=latest_status_subquery
        ).order_by('-id').order_by('-hot_lead')[offset : offset + limit]

        data = viewLeadFun(leadsData)
        if len(data) > 0:

            pagecount = math.ceil(ServiceCategory.objects.annotate( client_id=client_id_subquery,  client_name=client_name_subquery,  contact_number=contact_number_subquery,  alternate_contact_number=alternate_contact_number_subquery,  email_id=email_subquery, alternate_email_id=alternate_email_subquery, hot_lead = hot_lead_subquery, request_id = request_id_subquery, provider_id = provider_id_subquery, requester_id = requester_id_subquery, requester_location = requester_location_subquery, business_name = business_name_subquery, requester_sell_in_country = requester_sell_in_country_subquery, gst = gst_subquery, service_requester_type = service_requester_type_subquery, upload_date = upload_date_subquery, business_category = business_category_subquery, client_turnover = client_turnover_subquery, lead_owner = lead_owner_subquery, brand_name = brand_name_subquery, seller_address = seller_address_subquery, contact_preferences = contact_preferences_subquery, firm_type = firm_type_subquery, business_type = business_type_subquery, client_designation = client_designation_subquery, last_status_title=latest_status_subquery ).count()/limit)

            serializer = LeadsSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            if int(page) <= pagecount:
                return resFun(status.HTTP_200_OK, 'successful', {'data': serializer.data, 'total_pages': pagecount, "current_page": page, limit: limit})
            else :
                return resFun(status.HTTP_400_BAD_REQUEST, 'the page is unavailable', {'data': [], 'total_pages': pagecount, "current_page": page, limit: limit} )
        else:   
            return resFun(status.HTTP_400_BAD_REQUEST, 'no data found', {'data': [], 'total_pages': [], "current_page": page, limit: limit} )
        

        # return viewLeadBd_tl(user,offset,limit,page, None, None,user.department.title)
             





class ActiveCommercials(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceCreateActiveCommercialSerializer
    def get(self, request, program_id, format=None, *args, **kwargs):
        user = request.user
        if user.user_role.filter(title='super_admin').exists() or request.user.is_admin:
            res = commercialsWithPrograms('active', program_id)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized for this action', [])
        return res

class InactiveCommercials(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceCreateActiveCommercialSerializer
    def get(self, request, program_id, format=None, *args, **kwargs):
        user = request.user
        if user.user_role.filter(title='super_admin').exists() or request.user.is_admin:
            res = commercialsWithPrograms('archive', program_id)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized for this action', [])
        return res

def serviceCommercialAction(type, id):
    try:
        service_commercials = Commercials.objects.filter(id=id)
    except:
        return resFun(status.HTTP_400_BAD_REQUEST,'request failed',[])
    service_commercials=service_commercials.first()
    if type == 'archive':
        service_commercials.visibility = False
    elif type == 'restore':
        service_commercials.visibility = True
    service_commercials.save()
    return resFun(status.HTTP_200_OK,'archive successful',[])
    
class CommercialVisibility(GenericAPIView):
    serializer_class = ''
    permission_classes = [IsAuthenticated]
    def put(self, request, type, id ):
        if roleCheck(request.user, 'super_admin'):
            if type == 'archive':
                return  serviceCommercialAction('archive', id)
            elif type == 'restore':
                return serviceCommercialAction('restore', id)
        else:
            return resFun(status.HTTP_400_BAD_REQUEST,'you are not authorized for this action',[])


def commercialApproval(request, approval_type, lead_id, approvalStatus):
    try:
        service_category_instance = ServiceCategory.objects.get(commercial_approval__approval_type__title = approval_type, lead_id=lead_id)
    except:
        service_category_instance = None
    
    if service_category_instance != None:
        if approvalStatus == 'approved':

            commercials_check_instance = Commercials.objects.filter(commercials=service_category_instance.commercial_approval.commercial)
            commercials_check_instance = commercials_check_instance.first()
            
            if not commercials_check_instance:
                commercials_check_instance = Commercials.objects.create(**{"commercials":service_category_instance.commercial_approval.commercial })

            commercial_lead_instance = commercials_check_instance.lead_id.filter(lead_id=service_category_instance.lead_id)

            if not commercial_lead_instance.exists():
                commercials_check_instance.lead_id.add(service_category_instance)

            service_category_instance.program.commercials.add(commercials_check_instance)

            service_category_instance.commercial_approval.status = ApprovalStatus.objects.get(title='approved')

            if approval_type =='commercial' :
                status_instance = StatusHistory.objects.create(status=LeadStatus.objects.get(title='mou_pending'), updated_by=service_category_instance.associate, service_category=service_category_instance )
            elif approval_type =='foc' :
                status_instance = StatusHistory.objects.create(status=LeadStatus.objects.get(title='assign_associate_pending'), updated_by=service_category_instance.associate, service_category=service_category_instance )
            
            service_category_instance.status_history.add(status_instance)

            subject = f'commercial approved for lead id {service_category_instance.lead_id}'
            assoc_name = service_category_instance.associate.name if service_category_instance.associate else ''
            message = f'<h2>Hello {assoc_name},</h2></br><p>Commercial has been approved for lead id {service_category_instance.lead_id}. <a href="http://10.20.52.37:3000/lead_management">Click here to proceed further</a>.</p>'

            title = 'commercial_approved'
                        
        elif approvalStatus == 'rejected':
            service_category_instance.commercial_approval.status = ApprovalStatus.objects.get(title='rejected')
            status_instance = StatusHistory.objects.create(status=LeadStatus.objects.get(title='commercial_rejected'), updated_by=service_category_instance.associate, service_category=service_category_instance )
            service_category_instance.status_history.add(status_instance)

            subject = f'commercial rejected for lead id {service_category_instance.lead_id}'
            message = f'<h2>Hello {service_category_instance.associate.name if service_category_instance.associate else ''}</h2></br><p>Commercial has been rejected for lead id {service_category_instance.lead_id}. <a href="http://10.20.52.37:3000/lead_management">Click here to proceed further</a>.</p>'

            title = 'commercial_rejected'
        
        lead_history_instance = LeadHistory.objects.create( **{
            'title': title, 
            "field": [{ 'commercial': service_category_instance.commercial_approval.commercial }], 
            'action_type': ActionType.objects.filter(title=title).first(), 
            'updated_by': request.user
        })

        service_category_instance.history.add(lead_history_instance)

        if service_category_instance.associate:
            SendEmail([service_category_instance.associate.email], subject, message)

        service_category_instance.commercial_approval.save()
        return resFun(status.HTTP_200_OK, 'request successful', [])
    else:
        return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])    


class ApproveCommercial(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApproveCommercialSerializer
    def put(self, request, approval_type, lead_id):
        try:
            return commercialApproval(request, approval_type, lead_id, 'approved')

        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


class RejectCommercial(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RejectCommercialSerializer
    def put(self, request, approval_type, lead_id):
        try:
            return commercialApproval(request, approval_type, lead_id, 'rejected')
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


class LeadRelatedServices(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ViewAllServiceSerializer
    def get(self, request, client_id):
        try:
            leadsData = Leads.objects.select_related().filter(client_id=client_id, visibility = True).all()
            data = []
            for sd in leadsData:
                for s in sd.service_category.all():
                    d = {
                        "lead_id": s.lead_id,
                        'segment': {'id': s.program.marketplace.service.segment.id, "value": s.program.marketplace.service.segment.segment }  if s.program else {'id': None, "value": None },
                        'service': {'id': s.program.marketplace.service.id, "value": s.program.marketplace.service.service }  if s.program else {'id': None, "value": None },
                        'marketplace': {'id': s.program.marketplace.id, "value": s.program.marketplace.marketplace } if s.program else {'id': None, "value": None },
                        'program': {'id': s.program.id, "value": s.program.program } if s.program else {'id': None, "value": None },
                        "associate": {"id": s.associate.id if s.associate else None , "name": s.associate.name if s.associate else "-" }, 
                        "assigned_status": 'assigned' if s.associate != None else "not assigned", 
                        "payment_approval": s.payment_approval.title if s.payment_approval != None else "-", 
                        "commercial_approval": {"status": s.commercial_approval.status.title, "commercial": s.commercial_approval.commercial} if s.commercial_approval != None else {"status": '-', "commercial": '-'},
                        "commercial": s.commercials.commercials if s.commercials else "-",
                        "status": s.status_history.all().order_by('-id').first().status.title if s.status_history.all().exists() else "-",
                        "follow_up": [ {
                            'date':f.date if f.date else '-', 
                            'time': f.time if f.time else '-', 
                            'notes': f.notes if f.notes else '-', 
                            'created_by': f.created_by.name if f.created_by else '-' } for f in s.followup.all()],
                        } 

                    data.append(d)

            serializer = ViewAllServiceSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            return resFun(status.HTTP_200_OK, 'request successful', serializer.data )
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [e.detail] )
            

class LeadVisibility(GenericAPIView):
    serializer_class = LeadVisibilitySerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, type, id):
        try:
            if type == 'archive':
                return leadVisibilityFunc(request, id, True, 'lead archived successfully')
            elif type == 'restore':
                return leadVisibilityFunc(request, id, False, 'lead restored successfully')
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid request type', [])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [e.details])


def leadVisibilityFunc(request, id, visibility, message):
        user = request.user
        try:
            if roleCheck(user,'super_admin') or roleCheck(user,'admin'):
                lead = Leads.objects.get(id=id,visibility=visibility)
                lead.visibility = False if visibility == True else True
                lead.save()
                return resFun(status.HTTP_200_OK, message, [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized for this action',[])
        except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
        return res


class AddServiceCategory(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddServiceCategorySerializer
    def post(self, request, format=None, *args, **kwargs):
        try:
            if not request.data.get('client_id'):
                return resFun(status.HTTP_400_BAD_REQUEST, 'client id is a required field', [])
            
            client_instance = Leads.objects.filter(client_id = request.data.get('client_id')).first()
            if not client_instance:
                return resFun(status.HTTP_400_BAD_REQUEST, 'no client found', [])

            for p in request.data.get('program'):
                program_instance = Program.objects.filter(id=p, visibility=True)
                service_instance = ServiceCategory.objects.create(**{'lead_id': getLeadId(),'program': program_instance.first() })
                lead_history_instance = LeadHistory.objects.create(**{"action_type" : ActionType.objects.filter(title = 'created').first(),"title": 'service created',"updated_by" : request.user,})
                service_instance.history.add(lead_history_instance)
                status_history = StatusHistory.objects.create(**{'status': LeadStatus.objects.get(title='yet_to_contact'), 'updated_by': request.user, 'service_category': service_instance })      
                service_instance.status_history.add(status_history)
                client_instance.service_category.add(service_instance)
            return resFun(status.HTTP_200_OK, 'new service created, it will be assigned to the concerned department',[])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[e.detail])


class LeadStatusUpdate(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = LeadStatusUpdateSerializer
    def put(self, request, format=None, *args, **kwargs):
        try:
            if not request.data.get('lead_id'):
                return resFun(status.HTTP_400_BAD_REQUEST, 'lead id is required',[])
            if request.data.get('lead_status_id') == 0:
                pass
            else:
                if not request.data.get('lead_status_id'):
                    return resFun(status.HTTP_400_BAD_REQUEST, 'lead status id is required',[])
            
            service_category_instance = ServiceCategory.objects.get(lead_id = request.data.get('lead_id'))

            if service_category_instance:
                status_instance = LeadStatus.objects.get(id = request.data.get('lead_status_id'))
                status_history_instance = StatusHistory.objects.create(**{'status': status_instance, 'updated_by': request.user, 'service_category': service_category_instance  })
                service_category_instance.status_history.add(status_history_instance)
                service_category_instance.save()

                return resFun(status.HTTP_200_OK, 'successful',[])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'status not updated',[])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[e.detail])
        

class GetLeadHistory(GenericAPIView):
    serializer_class = LeadHIstorySerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, lead_id):
        try:
            leads_instance = Leads.objects.filter(service_category__lead_id = lead_id).first()
            service_category_instance = ServiceCategory.objects.filter(lead_id = lead_id).first()
            if leads_instance and service_category_instance :
                lead_history_instance = leads_instance.history.all().order_by('-id')
                service_category_history_instance = service_category_instance.history.all().order_by('-id')
                status_history_instance = service_category_instance.status_history.all().order_by('-id')
                followup_history_instance = service_category_instance.followup.all().order_by('-id')

                leads_data = [ {  
                        "action_type" : lh.action_type.title if lh.action_type else '',
                        "title": lh.title ,
                        "field" : lh.field ,
                        "previous": lh.previous ,
                        "new": lh.new ,
                        "date": lh.date.strftime('%d-%m-%Y %H:%M:%S.%f')[:-3],
                        "updated_by": lh.updated_by.name,
                    } for lh in lead_history_instance]
                
                service_category_data = [ {  
                        "action_type" : lh.action_type.title if lh.action_type else '',
                        "title": lh.title ,
                        "field" : lh.field ,
                        "previous": lh.previous,
                        "new": lh.new ,
                        "date": lh.date.strftime('%d-%m-%Y %H:%M:%S.%f')[:-3],
                        "updated_by": lh.updated_by.name,
                    } for lh in service_category_history_instance]
                
                status_data = [
                    {
                        "action_type" : 'status_update', 
                        "date" : sh.status_date.strftime('%d-%m-%Y %H:%M:%S.%f')[:-3],
                        "title" : 'status_update', 
                        "status" : sh.status.title, 
                        "updated_by" : sh.updated_by.name ,
                    } for sh in status_history_instance ]
                
                followup_data = [
                { 
                        "action_type" : 'follow_up', 
                        "title" : 'follow up scheduled', 
                        "date" : fh.created_date.strftime('%d-%m-%Y %H:%M:%S.%f')[:-3],
                        "followup_date" : fh.time.strftime('%d-%m-%Y %H:%M:%S.%f')[:-3],
                        "followup_time" : fh.time.strftime('%H:%M:%S'),
                        "notes" : fh.notes,
                        "updated_by" : fh.created_by.name,
                        "updated_by" : fh.created_by.name,
                    } for fh in followup_history_instance 
                ]

                print('service_category_data', service_category_data)

                leads_serializer  = LeadHIstorySerializer(data=leads_data, many=True)
                service_category_serializer  = LeadHIstorySerializer(data=service_category_data, many=True)
                status_serializer  = StatusSerializer(data=status_data, many=True)
                followup_serializer  = FollowupSerializer(data=followup_data, many=True)
                if leads_serializer.is_valid() and service_category_serializer.is_valid() and status_serializer.is_valid() and followup_serializer.is_valid():
                    data_to_sort = leads_serializer.data + service_category_serializer.data + status_serializer.data + followup_serializer.data
                    return resFun(status.HTTP_200_OK, 'request successful', sorted(data_to_sort, key = lambda x: datetime.strptime(x['date'], '%d-%m-%Y %H:%M:%S.%f'), reverse=True ) )
                else: 
                    return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', leads_serializer.errors + service_category_serializer.errors + status_serializer.errors + followup_serializer.errors )
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


class AddSubscriptionDuration(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddSubscriptionDurationSerializer
    def post(self, request, lead_id):
        try:
            try:
                service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])
            
            serializer  = AddSubscriptionDurationSerializer(service_category_instance, data=request.data, many=False)
            if serializer.is_valid():
                return resFun(status.HTTP_200_OK, 'request successful', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
            
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [e.detail])
        

class ServiceAssociateSubmit(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubmitServiceAssociateSerializer
    def post(self, request, lead_id):
        try:
            try:
                service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST,'lead id invalid', [])

            status_history_instance = StatusHistory.objects.create(**{'status': LeadStatus.objects.filter(title = 'subscription_started').first(), 'status_date': date.today() ,'updated_by': request.user, 'service_category': service_category_instance })
            service_category_instance.status_history.add(status_history_instance)
            service_category_instance.save()
            return resFun(status.HTTP_200_OK, 'request successful', [])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


class CreateFollowUp(GenericAPIView):
    serializer_class = CreateFollowUpSerializer
    permission_classes =[IsAuthenticated]
    def post(self, request):
        try:
            try:
                service_category_instance = ServiceCategory.objects.get(lead_id=request.data.get('lead_id'))
            except:
                service_category_instance = None

            if not request.data.get('lead_id'):
                return resFun(status.HTTP_400_BAD_REQUEST, 'lead id is mandatory field',[])
            if service_category_instance == None:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id',[])
            
            serializer = CreateFollowUpSerializer(data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer.instance.created_by = request.user
            serializer.instance.save()
            service_category_instance.followup.add(serializer.instance)

            if request.data.get('follow_up_type') == 'follow_up':
                status_instance = LeadStatus.objects.filter(title='follow_up').first()
            elif request.data.get('follow_up_type') == 'follow_up_proposal_sent':
                status_instance = LeadStatus.objects.filter(title='follow_up_proposal_sent').first()
            elif request.data.get('follow_up_type') == 'follow_up_unresponsive':
                status_instance = LeadStatus.objects.filter(title='follow_up_unresponsive').first()
            elif request.data.get('follow_up_type') == 'follow_up_seller_details_required':
                status_instance = LeadStatus.objects.filter(title='follow_up_seller_details_required').first()
            elif request.data.get('follow_up_type') == 'follow_up_mou_pending':
                status_instance = LeadStatus.objects.filter(title='follow_up_mou_pending').first()
            
            service_category_instance.status_history.add(StatusHistory.objects.create(**{'status': status_instance, 'updated_by': request.user, 'service_category': service_category_instance }))
            service_category_instance.save()

            return resFun(status.HTTP_200_OK, 'follow up created', [])
        
        except ValidationError as e: 
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


class AskForDetailEmail(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AskForDetailEmailSerializer
    def post(self, request):
        try:
            serializer = AskForDetailEmailSerializer(data=request.data, many=False)
            serializer.is_valid(raise_exception=True)

            print(serializer.data)

            lead_instance = Leads.objects.filter(client_id=serializer.data['client_id'])
            if lead_instance.exists():

                message = CannedEmail.objects.filter(email_type = 'ask_for_details').first()
                message = message.email
                message = str(message).replace("{***sender***}", request.user.name)
                email_id = lead_instance.first().email_id
                subject = 'Details required to proceed further with your onboarding with evitamin!'

                SendEmail([email_id], subject, message)

                service_category_instance = ServiceCategory.objects.filter(lead_id=request.data['lead_id']).first()
                status_history_instance = StatusHistory.objects.create(**{'status': LeadStatus.objects.get(title='follow_up_seller_details_required'), 'updated_by': request.user, 'service_category': service_category_instance })
                lead_history_instance = LeadHistory.objects.create( **{'title': 'asked for details', "field": [{ 'email': message }], 'action_type': ActionType.objects.filter(title='email_asked_for_details').first(), 'updated_by': request.user })
                service_category_instance.status_history.add(status_history_instance)
                service_category_instance.history.add(lead_history_instance)

                return resFun(status.HTTP_200_OK, "Email sent to the client, keep an eye on seller's response",[])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, "invalid client id",[])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, "something went wrong",[e.detail])
        

class PreviewMou(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PreviewMouSerializer
    def get(self, request, lead_id):
        try:
            try:
                service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
            except:
                service_category_instance = None
            if service_category_instance != None:
                try:
                    lead_instance = Leads.objects.get(service_category__id=service_category_instance.id)
                except:
                    lead_instance = None
                if lead_instance != None:
                    error_data = generate_mou_validation(service_category_instance, lead_instance)
                    if len(error_data) > 0:
                        return resFun(status.HTTP_400_BAD_REQUEST,', '.join(error_data)+', these fields are required, please update the seller details', [])
                    else:
                        res = generate_mou(service_category_instance, lead_instance)
                        return FileResponse(res.get('file'), content_type='application/pdf', as_attachment=True, filename=f'{lead_instance.business_name}.pdf')
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])
                            
def generate_mou_validation(service_category_instance, lead_instance):
    error_data = []
    if service_category_instance.commercials == None:
        error_data.append('commercial')
    if lead_instance.client_name == None:
        error_data.append('client name')
    if lead_instance.contact_number == None:
        error_data.append('contact number')
    if lead_instance.email_id == None:
        error_data.append('email id')   
    if lead_instance.business_name == None:
        error_data.append('business name')
    if lead_instance.brand_name == None:
        error_data.append('brand name')
    if lead_instance.gst == None:
        error_data.append('gst')
    if lead_instance.seller_address == None:
        error_data.append('seller address')
    if lead_instance.client_designation == None:
        error_data.append('client designation')
    return error_data

def generate_mou(service_category_instance, lead_instance ):
    client_name = lead_instance.client_name.capitalize()
    email_id = lead_instance.email_id
    phone_number = lead_instance.contact_number
    business_name = lead_instance.business_name.capitalize()
    brand_name = lead_instance.brand_name
    name_for_mou = client_name.capitalize()
    designation = lead_instance.client_designation.title.capitalize()
    gst = lead_instance.gst.upper()
    seller_address = lead_instance.seller_address
    commercial = service_category_instance.commercials.commercials.capitalize()
    template = get_template('mou/mou.html')
    date = datetime.now()
    date = f"{date.strftime('%d')}/{date.strftime('%m')}/{date.strftime('%Y')}"
    context = {
        'current_date': date,
        'business_name': business_name, 
        'brand_name': brand_name, 
        'business_address': seller_address, 
        "service_name": service_category_instance.program.marketplace.service.service, 
        "fees_slab": commercial, 
        "name_for_mou": name_for_mou, 
        'designation': designation, 
        'requester_name': client_name, 
        "email_id": email_id, 
        "gst": gst, 
        "phone_number": phone_number
        }
    html = template.render(context)
    res = BytesIO()
    result = pisa.CreatePDF(html, dest=res)
    if result.err:
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'error': 'error generating pdf',
            'data': []
            })
    res.seek(0)
    return {'file': res, 'service_category_instance': service_category_instance,  'lead_instance': lead_instance }


class EmailMou(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailMouSerializer
    def get(self, request, lead_id):
        try:
            try:
                service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
            except:
                service_category_instance = None
            if service_category_instance != None:
                try:
                    lead_instance = Leads.objects.get(service_category__id=service_category_instance.id)
                except:
                    lead_instance = None
                if lead_instance != None:
                    error_data = generate_mou_validation(service_category_instance, lead_instance)
                    if len(error_data) > 0:
                        return resFun(status.HTTP_400_BAD_REQUEST,', '.join(error_data)+', these fields are required, please update the seller details', [])
                    else:
                        res = generate_mou(service_category_instance, lead_instance)
                        email = lead_instance.email_id
                        subject = f'MOU for {service_category_instance.program.marketplace.service.service} with evitamin!'
                        text = 'PFA'
                        from_email = 'akshatnigamcfl@gmail.com'
                        recipient = [email]
                        email = EmailMultiAlternatives(subject, text, from_email, recipient)
                        email.attach_alternative('<h1>Hello</h1></br><p>Please seal & sign this MOU and revert back to the same email.</p>', 'text/html')
                        email.attach(lead_instance.business_name, res.get('file').read(), 'application/pdf')
                        email.send()
                        
                        lead_history_instance = LeadHistory.objects.create( **{'title': 'sent mou', "field": [{ 'email': text }], 'action_type': ActionType.objects.filter(title='email_mou').first(), 'updated_by': request.user })
                        service_category_instance.history.add(lead_history_instance)
                        
                        if email.send():
                            res = resFun(status.HTTP_200_OK,'email sent', [] )
                        else:
                            res = resFun(status.HTTP_400_BAD_REQUEST,'email not sent', [] )
                    return res
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


class UploadMouApproval(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UploadMouApprovalSerializer
    def post(self, request, lead_id):
        try:
            if request.FILES:
                try:
                    service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
                except:
                    service_category_instance = None

                if service_category_instance != None:
                    file = request.FILES['file']
                    service_category_instance.mou = file

                    status_history_instance = StatusHistory.objects.create(**{'status': LeadStatus.objects.get(title='payment_pending'), 'updated_by': request.user, 'service_category': service_category_instance })
                    lead_history_instance = LeadHistory.objects.create( **{'title': 'sent for mou approval', "field": [ { 'title' : 'sent to account department for approval' } ], 'action_type': ActionType.objects.filter(title='mou_sent_for_approval').first(), 'updated_by': request.user })
                    service_category_instance.status_history.add(status_history_instance)
                    service_category_instance.history.add(lead_history_instance)
                    service_category_instance.save()

                    return resFun(status.HTTP_200_OK, 'request successful', [])
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'file required to upload', [])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


class UploadPaymentProofApproval(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UploadFileSerializer
    def post(self, request, lead_id):
        try:
            if request.FILES:
                try:
                    service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
                except:
                    service_category_instance = None

                if service_category_instance != None:
                    file = request.FILES['file']
                    service_category_instance.payment_proof = file
                    service_category_instance.payment_approval = ApprovalStatus.objects.get(title='pending')
                    service_category_instance.status_history.add(StatusHistory.objects.create(**{'status': LeadStatus.objects.filter(title='payment_validation_pending').first(), 'updated_by': request.user, 'service_category': service_category_instance }))
                    service_category_instance.history.add(
                        LeadHistory.objects.create( **{
                            'title': 'sent for payment approval',
                            "field": [ { 'title' : 'sent to account department for approval' } ],
                            'action_type': ActionType.objects.filter(title='payment_proof_sent_for_approval').first(),
                            'updated_by': request.user
                        }))
                    service_category_instance.save()
                    res = resFun(status.HTTP_200_OK, 'request successful', [])
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'file required to upload', [])
            return res
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


class RaiseInvoice(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UploadFileSerializer
    def post(self, request, lead_id):
        try:
            try:
                service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
            except:
                service_category_instance = None
            if service_category_instance != None:
                service_category_instance.payment_approval = ApprovalStatus.objects.get(title='pending')
                service_category_instance.status_history.add(StatusHistory.objects.create(**{'status': LeadStatus.objects.filter(title='payment_validation_pending').first(), 'updated_by': request.user, 'service_category': service_category_instance }))
                service_category_instance.save()
                return resFun(status.HTTP_200_OK, 'request successful', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])
            

class ReasonSubmit(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReasonSubmitSerializer
    def put(self, request, table, format=None, *args, **kwargs):
        
        try:
            model = apps.get_model('dropdown', table)

            if request.data.get('status_id') == 0:
                pass
            else:
                if not request.data.get('status_id'):
                    return resFun(status.HTTP_400_BAD_REQUEST, 'id field is mandatory', [])
            
            if not request.data.get('client_id'):
                return resFun(status.HTTP_400_BAD_REQUEST, 'client id field is mandatory', [])
            
            if not request.data.get('lead_id'):
                return resFun(status.HTTP_400_BAD_REQUEST, 'lead id field is mandatory', [])

            id = request.data.get('status_id')
            client_id = request.data.get('client_id')
            lead_id = request.data.get('lead_id')

            lead_instance = Leads.objects.get(client_id=client_id, service_category__lead_id=lead_id)

            if table == 'not_interested':

                message = CannedEmail.objects.get(email_type='not_interested')
                message = message.email
                message = message.replace('{***reason***}', NotInterested.objects.get(id=id).title.lower())
                message = message.replace('{***contact_number***}', request.user.mobile_number)
                message = message.replace('{***email***}', request.user.email)
                message = message.replace('{***sender***}', request.user.name.upper())
                
                SendEmail([lead_instance.email_id], 'your service request was marked not interested', message)

                for ld in lead_instance.service_category.all():
                    if ld.lead_id == lead_id:
                        status_instance = LeadStatus.objects.get(title='not_interested')
                        # ld.status = status_instance
                        ld.not_interested_reason = NotInterested.objects.get(id=id)
                        # print(drp_lead_status.objects.get(title=''))
                        ld.save()
                        Status_history_instance = StatusHistory.objects.create(**{"status": status_instance, "updated_by": request.user, 'service_category': ld })
                        ld.status_history.add(Status_history_instance)
                        status_update = True

                if status_update:
                    res = resFun(status.HTTP_200_OK, 'saved successfully',[])
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'status not updated',[])

            elif table == 'unresponsive':

                for ld in lead_instance.service_category.all():
                    if ld.lead_id == lead_id:
                        unresponsive_list = []
                        lead_status_list = ld.status_history.all().order_by('-id')

                        for i in range(5):
                            print(lead_status_list[i])
                            if lead_status_list[i].status.title == 'follow_up_unresponsive':
                                unresponsive_list.append('follow_up_unresponsive')

                        if len(unresponsive_list) >=5:
                           message = CannedEmail.objects.get(email_type='dead_lead')
                        else :        
                           message = CannedEmail.objects.get(email_type='unresponsive')
            
                        message = message.email
                        message = message.replace('{***reason***}', Unresponsive.objects.get(id=id).title.lower())

                        if not len(unresponsive_list) >=5:
                            message = message.replace('{***date***}', '00/00/0000')
                        
                        message = message.replace('{***contact_number***}', request.user.mobile_number)
                        message = message.replace('{***email***}', request.user.email)
                        message = message.replace('{***sender***}', request.user.name.upper())
                        
                        SendEmail([lead_instance.email_id], 'your service request was marked unresponsive', message)

                        for ld in lead_instance.service_category.all():
                            if ld.lead_id == lead_id:
                                if len(unresponsive_list) >=5:
                                    status_instance = LeadStatus.objects.get(title='dead_lead')
                                else:
                                    status_instance = LeadStatus.objects.get(title='follow_up_unresponsive')
                                ld.unresponsive_reason = Unresponsive.objects.get(id=id)
                                ld.save()
                                Status_history_instance = StatusHistory.objects.create(**{"status": status_instance, "updated_by": request.user, 'service_category': ld })
                                ld.status_history.add(Status_history_instance)
                                status_update = True
                        if status_update:
                            final_status = [ {'lead_status': status_instance.title} ]
                            res = resFun(status.HTTP_200_OK, 'saved successfully', final_status)
                        else:
                            res = resFun(status.HTTP_400_BAD_REQUEST, 'status not updated',[])

            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'table out of range',[])
            return res
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])


class LeadsSearch(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeadsSerializer
    def get(self, request, attribute, data, format=None, *args, **kwargs):
        res = viewLeadSeachFun(request, attribute, data, True)
        return res


def viewLeadSeachFun(request, attribute, data, visibility):
        user = request.user        
        main_data = data.replace('_',' ')

        if roleCheck(user,'super_admin') or roleCheck(user,'admin') or roleCheck(user,'business_development_associate') or roleCheck(user,'business_development_team_lead') or user.is_admin:

            client_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_id')[:1])
            client_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_name')[:1])
            contact_number_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('contact_number')[:1])
            alternate_contact_number_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('alternate_contact_number')[:1])
            email_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('email_id')[:1])
            alternate_email_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('alternate_email_id')[:1])
            hot_lead_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('hot_lead')[:1])
            request_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('request_id')[:1])
            provider_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('provider_id')[:1])
            requester_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_id')[:1])
            requester_location_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_location')[:1])
            business_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_name')[:1])
            requester_sell_in_country_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_sell_in_country')[:1])
            gst_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('gst')[:1])
            service_requester_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('service_requester_type')[:1])
            upload_date_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('upload_date')[:1])
            
            business_category_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_category__id')[:1])
            business_category_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_category')[:1])

            client_turnover_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_turnover__id')[:1])
            client_turnover_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_turnover__title')[:1])
            
            lead_owner_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('lead_owner__id')[:1])
            lead_owner_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('lead_owner__name')[:1])

            brand_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('brand_name')[:1])
            seller_address_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('seller_address')[:1])

            contact_preferences_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('contact_preferences')[:1])
            firm_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('firm_type')[:1])
            business_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_type')[:1])
            
            client_designation_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_designation__id')[:1])
            client_designation_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_designation__title')[:1])

            latest_status_id_subquery = Subquery(StatusHistory.objects.filter(service_category=OuterRef('pk')).order_by('-id').values('status__id')[:1])
            latest_status_subquery = Subquery(StatusHistory.objects.filter(service_category=OuterRef('pk')).order_by('-id').values('status__title')[:1])
    
            query = Q()
            query_program = Q()

            if roleCheck(user,'business_development_associate') or roleCheck(user,'business_development_team_lead'):
                query_program |= Q(program__in=user.program.all())

            if attribute == 'client_id':
                print('client_id', data)
                query |= Q(client_id__icontains = main_data)
            elif attribute == 'lead_id': 
                query |= Q(lead_id = main_data)
            elif attribute == 'client_name':
                query |= Q(client_name__icontains = main_data)
            elif attribute == 'contact_number': 
                query |= Q(contact_number__icontains = main_data)
            elif attribute == 'email_id': 
                query |= Q(email_id__icontains = main_data)
            else:
                return resFun(status.HTTP_400_BAD_REQUEST,'invalid search attribute',[])

            leads = ServiceCategory.objects.annotate(
                client_id=client_id_subquery, 
                client_name=client_name_subquery, 
                contact_number=contact_number_subquery, 
                alternate_contact_number=alternate_contact_number_subquery,
                email_id=email_subquery,
                alternate_email_id=alternate_email_subquery,
                hot_lead = hot_lead_subquery,
                request_id = request_id_subquery,
                provider_id = provider_id_subquery,
                requester_id = requester_id_subquery,
                requester_location = requester_location_subquery,
                business_name = business_name_subquery,
                requester_sell_in_country = requester_sell_in_country_subquery,
                gst = gst_subquery,
                service_requester_type = service_requester_type_subquery,
                upload_date = upload_date_subquery,

                business_category_id = business_category_id_subquery,
                business_category = business_category_subquery,

                client_turnover_id = client_turnover_id_subquery,
                client_turnover = client_turnover_subquery,

                lead_owner_id = lead_owner_id_subquery,
                lead_owner = lead_owner_subquery,

                brand_name = brand_name_subquery,
                seller_address = seller_address_subquery,

                contact_preferences = contact_preferences_subquery,
                firm_type = firm_type_subquery,
                business_type = business_type_subquery,

                client_designation_id = client_designation_id_subquery,
                client_designation = client_designation_subquery,
                
                last_status_id=latest_status_id_subquery,
                last_status_title=latest_status_subquery,
            ).filter(query).filter(query_program).order_by('-hot_lead').order_by('-id')

            res = viewLeadBd_tl(user,None,None,None, leads, attribute, user.user_role.first())
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'you are not authorized to view this data',[])
        return res


class UpdatePaymentStatus(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalSerializer
    def post(self, request, lead_id, payment_approval_status):
        try:
            try:
                Service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
            except:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [])
            try:
                approval_status_instance  = ApprovalStatus.objects.get(title = payment_approval_status)
            except:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'invalid status', [])

            Service_category_instance.payment_approval = approval_status_instance
            if payment_approval_status == 'approved':
                Service_category_instance.status_history.add(StatusHistory.objects.create(**{'status': LeadStatus.objects.filter(title='assign_associate_pending').first(), 'updated_by': request.user, 'service_category': Service_category_instance }))
            else:
                Service_category_instance.status_history.add(StatusHistory.objects.create(**{'status': LeadStatus.objects.filter(title='payment_pending').first(), 'updated_by': request.user, 'service_category': Service_category_instance }))

            Service_category_instance.save()

            res = resFun(status.HTTP_200_OK, 'request successful', [])
            return res
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])


def viewLeadBd_tl(user, offset, limit, page, data, attribute, user_role):
    
    if user_role == 'business_development_team_lead' or user_role == 'business_development_team_lead' and   len(user.program.all()) == 0:
        return resFun(status.HTTP_400_BAD_REQUEST, 'contact user manager to assign you atleast one program', [])
    
    data = viewLeadFun(data, user_role)
    
    if len(data) > 0:
        serializer = LeadsSerializer(data=data, many=True)
        if serializer.is_valid():
            res = resFun(status.HTTP_200_OK,'successful',serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'request failed',serializer.errors)
    else:
        res = resFun(status.HTTP_204_NO_CONTENT, 'no data found', [] )
    return res


def viewLeadFun(leadsData):
    data = []
    for sd in leadsData:
        tat = TurnArroundTime.objects.all().first()
        today = datetime.now()
        upload_date = datetime.strptime(str(sd.upload_date),"%Y-%m-%d %H:%M:%S.%f%z")
        upload_date = upload_date.replace(tzinfo=None)
        deadline = (today - upload_date).total_seconds()
        deadline = (math.ceil((int(tat.duration_in_hrs) - math.floor(int(deadline // (3600)))) / 24) -1 )


        data.append({
                'id' : sd.id , 
                'client_id' : sd.client_id , 
                'client_name': sd.client_name, 
                'contact_number': sd.contact_number,
                'alternate_contact_number': sd.alternate_contact_number if sd.alternate_contact_number else '-',
                'email_id': sd.email_id,
                'alternate_email_id': sd.alternate_email_id if sd.alternate_email_id else '-',
                'gst': sd.gst if sd.gst else '-',
                'seller_address': sd.seller_address if sd.seller_address else '-',
                "contact_preferences" : sd.contact_preferences.title if sd.contact_preferences else '-',
                "firm_type" : sd.firm_type.title if sd.firm_type else '-',
                "request_id": sd.request_id if sd.request_id else '-',
                "provider_id": sd.provider_id if sd.provider_id else '-',
                "requester_id": sd.requester_id if sd.requester_id else '-',
                "requester_location": sd.requester_location if sd.requester_location else '-',
                "requester_sell_in_country": sd.requester_sell_in_country if sd.requester_sell_in_country else '-',
                "service_requester_type": sd.service_requester_type if sd.service_requester_type else '-',
                "lead_owner": { 'id': UserAccount.objects.filter(id=sd.lead_owner).first().id, 'name': UserAccount.objects.filter(id=sd.lead_owner).first().name} if sd.lead_owner else { 'id': None , 'name': '-' },
                "client_turnover" : { 'id': sd.client_turnover_id, 'value': sd.client_turnover } if sd.client_turnover else { 'id': None, 'value': ''},
                "client_designation" : { 'id': sd.client_designation, 'value':  sd.client_designation} if sd.client_designation else { 'id': None, 'value': ''},
                "business_name" : sd.business_name if sd.business_name else '-',
                "brand_name" : sd.brand_name if sd.brand_name else '-',
                "business_type" : sd.business_type.title if sd.business_type else '-',
                "business_category" : { 'id' : sd.business_category_id, 'value': sd.business_category} if sd.business_category else { 'id': None, 'value': ''},
                'upload_date': upload_date , 
                'deadline': deadline,
                        "program": { 'id': sd.program.id, 'value': sd.program.program} if sd.program else { 'id': None, 'value': None},
                        "lead_id": sd.lead_id,
                        'marketplace': { 'id':sd.program.marketplace.id, 'value': sd.program.marketplace.marketplace} if sd.program else { 'id': None, 'value': None}, 
                        'service': { 'id': sd.program.marketplace.service.id, 'value': sd.program.marketplace.service.service} if sd.program else { 'id': None, 'value': None}, 
                        'segment': { 'id': sd.program.marketplace.service.segment.id, 'value': sd.program.marketplace.service.segment.segment} if sd.program else { 'id': None, 'value': None}, 
                        "associate": {"id": sd.associate.id if sd.associate else None , "name": sd.associate.name if sd.associate else None }, 
                        "assigned_status": 'assigned' if sd.associate != None else "not assigned", 
                        "payment_approval": sd.payment_approval.title if sd.payment_approval != None else "-", 
                        "commercial_approval": {"status": sd.commercial_approval.status.title, "commercial": sd.commercial_approval.commercial} if sd.commercial_approval != None else {"status": '-', "commercial": '-'},
                        "commercial": sd.commercials.id if sd.commercials else None,
                        "status": {'id': sd.last_status_id, 'value': sd.last_status_title.replace('_',' ') } if sd.status_history.all().exists() else {"id": None, 'value': None},
                        "follow_up": [ {
                            'date':f.date if f.date else '-', 
                            'time': f.time if f.time else '-', 
                            'notes': f.notes if f.notes else '-', 
                            'created_by': f.created_by.name if f.created_by else '-' } for f in sd.followup.all()],
                        "payment_model": { 'id': sd.program.payment_model.id, 'value': sd.program.payment_model.title} if sd.program and sd.program.payment_model  else { 'id': None, 'value': None},
                        "payment_terms": { 'id': sd.program.payment_terms.id, 'value': sd.program.payment_terms.title} if sd.program and sd.program.payment_terms  else { 'id': None, 'value': None},
                        "paid_by": { 'id': sd.program.paid_by.id, 'value': sd.program.paid_by.title} if sd.program and sd.program.paid_by  else { 'id': None, 'value': None},
                        "mou_required": sd.program.mou_required  if sd.program and sd.program.mou_required  else None,
                        "comments": sd.program.comments  if sd.program and sd.program.comments  else None,

                "hot_lead" : sd.hot_lead
                })
    return data




class AssignAssociate(GenericAPIView):
    serializer_class = AssignAssociateSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, format=None, *args, **kwargs):

        user_id = request.data.get('user_id')
        lead_id = request.data.get('lead_id')
        try:
            userData = UserAccount.objects.get(id = user_id, visibility=True)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'user not found', [])
        
        def updateHistory(data):
            lead_history_data = []
            if data.associate != userData:
                lead_history_data.append({ 
                    'key': 'associate',
                    'previous': data.associate.name if data.associate != None else '',  
                    'new': userData.name 
                })
            return lead_history_data
        
        if isinstance(lead_id, list):
            for ld in lead_id:
                data = ServiceCategory.objects.get(lead_id= ld)
                if data: 
                    title = 'assigned' if data.associate == None else 'reassigned'
                    lead_history_data = updateHistory(data)
                    serializer = AssignAssociateSerializer(data, data={'associate': user_id}, partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        lead_history_instance = LeadHistory.objects.create( **{
                            'title': title,
                            "field": lead_history_data, 
                            'action_type': ActionType.objects.filter(title=title).first(), 
                            'updated_by': request.user
                        })
                        data.history.add(lead_history_instance)
                        res = resFun(status.HTTP_200_OK,'associate assigned', [])
                    else:
                        res = resFun(status.HTTP_400_BAD_REQUEST,'request failed', [])
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST,'invalid lead id', [])
        else: 
            data = ServiceCategory.objects.get(lead_id= lead_id)
            if data: 
                title = 'assigned' if data.associate == None else 'reassigned'
                lead_history_data = updateHistory(data)
                serializer = AssignAssociateSerializer(data, data={'associate': user_id}, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    lead_history_instance = LeadHistory.objects.create( **{
                        'title': title,
                        "field": lead_history_data, 
                        'action_type': ActionType.objects.filter(title=title).first(), 
                        'updated_by': request.user
                    })
                    data.history.add(lead_history_instance)
                    res = resFun(status.HTTP_200_OK,'associate assigned', [])
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST,'request failed', [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'invalid lead id', [])
        return res
  

def proposalEmail(request):
    if len(request.data.get('lead_id')) >= 10:
        return resFun(status.HTTP_400_BAD_REQUEST, "more than 10 emails can't be sent at once", [])
                
    commercial_id = request.data.get('commercial_id')
    if commercial_id == None:
        if not request.data.get('lead_id'):
            return resFun(status.HTTP_400_BAD_REQUEST, 'lead id is required', [])
        if not request.data.get('custom_commercial'):
            return resFun(status.HTTP_400_BAD_REQUEST, 'custom commercial is required', [])
        
        for lead_id in request.data.get('lead_id'):
            service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
            if service_category_instance.associate == None:
                service_category_instance.associate = request.user
            commercial_approval_instance = CommercialApproval.objects.create(**{"commercial": request.data.get('custom_commercial'), 'status': ApprovalStatus.objects.get(title='pending'), 'approval_type': ApprovalType.objects.get(title='commercial'), 'service_category': service_category_instance  })
            service_category_instance.commercial_approval = commercial_approval_instance
            service_category_instance.status_history.add(StatusHistory.objects.create(**{'status': LeadStatus.objects.filter(title='commercial_approval_pending').first(), 'updated_by': request.user, 'service_category': service_category_instance }))
            # service_category_instance.status = Status_history.objects.create(**{'status': drp_lead_status.objects.filter(title='pending for commercial approval'), 'updated_by': request.user.name })
            service_category_instance.save()
            super_admin_instance = UserAccount.objects.filter(user_role__title='super_admin')
            print('super_admin_instance', list(super_admin_instance.values_list('email', flat=True)))
            SendEmail(super_admin_instance.values_list('email', flat=True), 'Commercial Approval Pending', f'''<h3>Hello,</h3></br><p><b>{request.user.name}</b> from <b>{request.user.user_role.first()}</b> has requested you to approve a commercial. Check commercial details below</p></br>
                    <table class="table table-zebra" style="border: 1px solid black; border-collapse:collapse" border="1>
                        <thead>
                          <tr>
                            <th style="border: 1px solid black;">Segment</th>
                            <th style="border: 1px solid black;">Service</th>
                            <th style="border: 1px solid black;">Marketplace</th>
                            <th style="border: 1px solid black;">Commercial</th>
                            <th style="border: 1px solid black;">Requested By</th>
                          </tr>
                        </thead>
                        <tbody>
                            <tr>
                              <td style="border: 1px solid black;">{service_category_instance.program.marketplace.service.segment.segment}</td>
                              <td style="border: 1px solid black;">{service_category_instance.program.marketplace.service.service}</td>
                              <td style="border: 1px solid black;">{service_category_instance.program.marketplace.marketplace}</td>
                              <td style="border: 1px solid black;">{request.data.get('custom_commercial')}</td>
                              <td style="border: 1px solid black;">{request.user.name}</td>
                            </tr>
                        </tbody>
                        </table>
                        </br>
                        <p>Please click link below to approve commercial</p>
                        <p><b>Regards,</b></p>
                      ''')
            
            lead_history_instance = LeadHistory.objects.create( **{
                'title': 'commercial sent for approval', 
                "field": [{ 'sent_to': ','.join(super_admin_instance.values_list('email', flat=True)), 'commercial': request.data.get('custom_commercial') }], 
                'action_type': ActionType.objects.filter(title='commercial_sent_for_approval').first(), 
                'updated_by': request.user
            })
            service_category_instance.history.add(lead_history_instance)
            return resFun(status.HTTP_200_OK, 'commercial sent for approval, you will be notified once approved', [])
 
    else:
        if isinstance(request.data.get('lead_id'), list):
            sent = []
            not_sent = []

        for lead_id in request.data.get('lead_id'):
            lead_instance = Leads.objects.get(service_category__lead_id=lead_id, visibility=True)
            email = lead_instance.email_id
            try:
                service = Commercials.objects.get(id=commercial_id)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid commercial id', [] )
                        
            try:
                service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [] )


            program = service_category_instance.program
                        
            if not program:
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])
                        
            try:
                message = ProposalEmail.objects.get(program = program)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'no proposal found, please contact admin', [] )
                        
            message = message.email
            # bank_details = ev_bank_details.objects.all().first()
            # account_name = bank_details.account_name
            # bank_name = bank_details.bank_name
            # account_number = bank_details.account_number
            # ifsc = bank_details.ifsc
            # print(message)
            # message = message.replace('{***account_name***}', account_name)
            # message = message.replace('{***bank_name***}', bank_name)
            # message = message.replace('{***account_number***}', account_number)
            # message = message.replace('{***ifsc_code***}', ifsc)
            message = message.replace('{***service***}', program.marketplace.service.service)
            message = message.replace('{***slab***}', Commercials.objects.get(id=commercial_id).commercials)
            message = message.replace('{***sender***}', request.user.name)
              
            subject = 'service proposal from evitamin'  
            from_email = 'akshatnigamcfl@gmail.com'
            recipient_list = [email]
            text = 'email sent from MyDjango'
            print(recipient_list)
            email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
            email.attach_alternative(message, 'text/html')
            email.send()
            if email:
                service_category_instance.commercials = Commercials.objects.get(id=commercial_id)
                service_category_instance.save()
                status_history_instance = StatusHistory.objects.create(**{'status': LeadStatus.objects.get(title='follow_up_proposal_sent'), 'updated_by': request.user, 'service_category': service_category_instance })
                lead_history_instance = LeadHistory.objects.create( **{'title': 'sent proposal', "field": [{ 'email': message }], 'action_type': ActionType.objects.filter(title='email_proposal').first(), 'updated_by': request.user })
                service_category_instance.status_history.add(status_history_instance)
                service_category_instance.history.add(lead_history_instance)
                sent.append(lead_id)
            else:
                not_sent.append(lead_id)
  
        else:
            return resFun(status.HTTP_200_OK, 'email sent', [{'sent': sent, 'not_sent': not_sent}] )


class EmailProposal(GenericAPIView):
    serializer_class = EmailProposalSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None, *args, **kwargs):
        try:
            
            client_id = request.data.get('client_id')
            commercial_id = request.data.get('commercial_id')
            lead_id = request.data.get('lead_id')

            if commercial_id == None:

                if not lead_id:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'lead id is required', [])
                if not request.data.get('custom_commercial'):
                    return resFun(status.HTTP_400_BAD_REQUEST, 'custom commercial is required', [])
                
                service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
                if service_category_instance.associate == None:
                    service_category_instance.associate = request.user
                commercial_approval_instance = CommercialApproval.objects.create(**{"commercial": request.data.get('custom_commercial'), 'status': ApprovalStatus.objects.get(title='pending'), 'approval_type': ApprovalType.objects.get(title='commercial'), 'service_category': service_category_instance  })
                service_category_instance.commercial_approval = commercial_approval_instance
                service_category_instance.status_history.add(StatusHistory.objects.create(**{'status': LeadStatus.objects.filter(title='commercial_approval_pending').first(), 'updated_by': request.user, 'service_category': service_category_instance }))
                # service_category_instance.status = Status_history.objects.create(**{'status': drp_lead_status.objects.filter(title='pending for commercial approval'), 'updated_by': request.user.name })
                service_category_instance.save()
                super_admin_instance = UserAccount.objects.filter(user_role__title='super_admin')
                print('super_admin_instance', list(super_admin_instance.values_list('email', flat=True)))
                SendEmail(super_admin_instance.values_list('email', flat=True), 'Commercial Approval Pending', f'''<h3>Hello,</h3></br><p><b>{request.user.name}</b> from <b>{request.user.user_role.first()}</b> has requested you to approve a commercial. Check commercial details below</p></br>
                        <table class="table table-zebra" style="border: 1px solid black; border-collapse:collapse" border="1>
                            <thead>
                            <tr>
                                <th style="border: 1px solid black;">Segment</th>
                                <th style="border: 1px solid black;">Service</th>
                                <th style="border: 1px solid black;">Marketplace</th>
                                <th style="border: 1px solid black;">Commercial</th>
                                <th style="border: 1px solid black;">Requested By</th>
                            </tr>
                            </thead>
                            <tbody>
                                <tr>
                                <td style="border: 1px solid black;">{service_category_instance.program.marketplace.service.segment.segment}</td>
                                <td style="border: 1px solid black;">{service_category_instance.program.marketplace.service.service}</td>
                                <td style="border: 1px solid black;">{service_category_instance.program.marketplace.marketplace}</td>
                                <td style="border: 1px solid black;">{request.data.get('custom_commercial')}</td>
                                <td style="border: 1px solid black;">{request.user.name}</td>
                                </tr>
                            </tbody>
                            </table>
                            </br>
                            <p>Please click link below to approve commercial</p>
                            <p><b>Regards,</b></p>
                        ''')
                
                lead_history_instance = LeadHistory.objects.create( **{
                    'title': 'commercial sent for approval', 
                    "field": [{ 'sent_to': ','.join(super_admin_instance.values_list('email', flat=True)), 'commercial': request.data.get('custom_commercial') }], 
                    'action_type': ActionType.objects.filter(title='commercial_sent_for_approval').first(), 
                    'updated_by': request.user
                })
                service_category_instance.history.add(lead_history_instance)
                return resFun(status.HTTP_200_OK, 'commercial sent for approval, you will be notified once approved', [])
                

            else:
                lead_instance = Leads.objects.get(client_id=client_id, visibility=True)
                email = lead_instance.email_id
                try:
                    service = Commercials.objects.get(id=commercial_id)
                except:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'invalid commercial id', [] )
                try:
                    service_category_instance = ServiceCategory.objects.get(lead_id=lead_id)
                except:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'invalid lead id', [] )

                program = service_category_instance.program

                if not program:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])


                try:
                    message = ProposalEmail.objects.filter(program = program).first()
                    if not message:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'no proposal found, please contact admin', [] )
                except:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'no proposal found, please contact admin', [] )

                message = message.email
                # bank_details = ev_bank_details.objects.all().first()
                # account_name = bank_details.account_name
                # bank_name = bank_details.bank_name
                # account_number = bank_details.account_number
                # ifsc = bank_details.ifsc
                # print(message)
                # message = message.replace('{***account_name***}', account_name)
                # message = message.replace('{***bank_name***}', bank_name)
                # message = message.replace('{***account_number***}', account_number)
                # message = message.replace('{***ifsc_code***}', ifsc)
                message = message.replace('{***service***}', program.marketplace.service.service)
                message = message.replace('{***slab***}', Commercials.objects.get(id=commercial_id).commercials)
                message = message.replace('{***sender***}', request.user.name)
                subject = 'service proposal from evitamin'  
                from_email = 'akshatnigamcfl@gmail.com'
                recipient_list = [email]
                text = 'email sent from MyDjango'
                print(recipient_list)
                email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
                email.attach_alternative(message, 'text/html')
                email.send()
                if email:                    
                    service_category_instance.commercials = Commercials.objects.get(id=commercial_id)
                    service_category_instance.save()
                    status_history_instance = StatusHistory.objects.create(**{'status': LeadStatus.objects.get(title='follow_up_proposal_sent'), 'updated_by': request.user, 'service_category': service_category_instance })
                    lead_history_instance = LeadHistory.objects.create( **{'title': 'sent proposal', "field": [{ 'email': message }], 'action_type': ActionType.objects.filter(title='email_proposal').first(), 'updated_by': request.user })
                    service_category_instance.status_history.add(status_history_instance)
                    service_category_instance.history.add(lead_history_instance)

                    return resFun(status.HTTP_200_OK, 'email sent', [])
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'email not sent', [] )        
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail] )


class BulkActionLead(GenericAPIView):
    serializer_class = BulkActionSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, type):
        try:
            if type == 'assign_associate':
                pass
            elif type == 'email_proposal':
                return proposalEmail(request)
            elif type == 'update_status':

                if len(request.data.get('lead_id')) == 0:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'lead id is required',[])
                if request.data.get('lead_status_id') == 0:
                    pass
                else:
                    if not request.data.get('lead_status_id'):
                        return resFun(status.HTTP_400_BAD_REQUEST, 'lead status id is required',[])

                for lead_id in request.data.get('lead_id'):
                    lead_instance = Leads.objects.get(service_category__lead_id =lead_id)
                    for ld in lead_instance.service_category.all():
                        if ld.lead_id == lead_id:
                            status_instance = LeadStatus.objects.get(id = request.data.get('lead_status_id'))
                            ld.save()
                            service_category = lead_instance.service_category.filter(lead_id=lead_id).first()
                            status_history_instance = StatusHistory.objects.create(**{'status': status_instance, 'updated_by': request.user, 'service_category': service_category  })
                            service_category.status_history.add(status_history_instance)
                return resFun(status.HTTP_200_OK, 'request successful',[])
                
            elif type == 'add_remark':

                if len(request.data.get('lead_id')) == 0:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'lead id is required',[])
                if request.data.get('remark') == 0:
                    pass
                else:
                    if not request.data.get('remark'):
                        return resFun(status.HTTP_400_BAD_REQUEST, 'remark is required',[])
                for lead_id in request.data.get('lead_id'):
                    lead_instance = Leads.objects.get(service_category__lead_id =lead_id)
                    for ld in lead_instance.service_category.all():
                        if ld.lead_id == lead_id:
                            service_category = lead_instance.service_category.filter(lead_id=lead_id).first()
                            remark_instance = RemarkHistory.objects.create(**{ 'remark': request.data.get('remark'), 'lead_id': service_category })
                            service_category.remark.add(remark_instance)
                return resFun(status.HTTP_200_OK, 'request successful',[])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid request type', [])

        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [e.detail])





class CreateServices(GenericAPIView):
    serializer_class = CreateSegmentSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, type):
        if roleCheck(request.user,'super_admin') or request.user.is_admin:
            if type == 'segment':
                try:
                    segment = Segment.objects.filter(segment = request.data.get('segment').lower()).values()
                except:
                    segment = Segment.objects.filter(pk__in = []).values()
                if not segment.exists():
                    serializer = CreateSegmentSerializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return resFun(status.HTTP_200_OK, 'added successfully',serializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'segment already exists, kindly check archives',[])
            
            elif type == 'service':
                try:
                    segment = Service.objects.filter(segment=int(request.data.get('segment')), service = request.data.get('service').lower()).values()
                except:
                    segment = Service.objects.filter(pk__in = []).values()
                
                if not segment.exists():
                    serializer = CreateServiceSerializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        marketplace_instance =  Marketplace.objects.create(**{'service': serializer.instance, 'marketplace': 'generic' })
                        Program.objects.create(**{'marketplace': marketplace_instance ,'program': 'regular', 'mou_required': True, 'comments': ''})
                        return resFun(status.HTTP_200_OK, 'added successfully',serializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'service already exists, kindly check archives',[])

            elif type == 'marketplace':
                marketplace = Marketplace.objects.filter(service=int(request.data.get('service')), marketplace = request.data.get('marketplace').lower()).values()
                if not marketplace.exists():
                    serializer = CreateMarketplaceSerializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        Program.objects.create(**{'marketplace': serializer.instance ,'program': 'regular', 'mou_required': True, 'comments': ''})
                        return resFun(status.HTTP_200_OK, 'added successfully', serializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'marketplace already exists, kindly check archives', [])
            elif type == 'program':
                segment = Program.objects.filter(marketplace = int(request.data.get('marketplace')), program = request.data.get('program').lower()).values()
                if not segment.exists():
                    serializer = CreateProgramSerializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return resFun(status.HTTP_200_OK, 'added successfully', serializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'program already exists, kindly check archives', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid request', [])
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized for this action',[])

class UpdateServices(GenericAPIView):
    serializer_class = CreateSegmentSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, type, id):
        try:
            if roleCheck(request.user,'super_admin') or request.user.is_admin:
                if type == 'segment':
                    segment_validation = Segment.objects.filter(segment=request.data.get('segment'))
                    if segment_validation.exists():
                        if segment_validation.first().id != id:
                            return resFun(status.HTTP_400_BAD_REQUEST, 'segment already exists', [])
                        else:
                            pass

                    try:
                        segment = Segment.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'segment not found', [])

                    serializer = ViewSegmentSerializer(segment.first(), data=request.data, partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
                    
                elif type == 'service':
                    service_validation = Service.objects.filter(marketplace__id=int(request.data.get('segment')), service=request.data.get('service'))
                    if service_validation.exists():
                        if service_validation.first().id != id:
                            return resFun(status.HTTP_400_BAD_REQUEST, 'service already exists', [])
                        else:
                            pass
                    try:
                        service = Service.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'service not found', [])

                    serializer = ViewServiceSerializer(service.first(), data=request.data, partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
                    else:
                        print(serializer.errors)
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)

                elif type == 'marketplace':
                    marketplace_validation = Marketplace.objects.filter(service__id=int(request.data.get('service')), marketplace=request.data.get('marketplace'))
                    if marketplace_validation.exists():
                        if marketplace_validation.first().id != id:
                            return resFun(status.HTTP_400_BAD_REQUEST, 'marketplace already exists', [])

                    try:
                        marketplace = Marketplace.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'marketplace not found', [])
                    serializer = ViewMarketplaceSerializer(marketplace.first(), data=request.data, partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
                elif type == 'program':
                    program_validation = Program.objects.filter(marketplace__id=int(request.data.get('marketplace')), program=request.data.get('program'))
                    if program_validation.exists():
                        if program_validation.first().id != id:
                            return resFun(status.HTTP_400_BAD_REQUEST, 'program already exists', [])

                    try:
                        program = Program.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'program not found', [])

                    if program.exists():
                        serializer = ProgramSerializer(program.first(), data=request.data, partial=True)
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()

                            if request.data.get('commercials'):
                                def createCommercial(commercial):
                                        serializer.instance.commercials.add(Commercials.objects.create(commercials = commercial))

                                for c in request.data.get('commercials'):
                                    commercial_value_instance = Commercials.objects.filter(commercials = c['value']).first()

                                    if c['id'] == None:
                                        if commercial_value_instance:
                                            commercial_value_instance.visibility = True
                                            commercial_value_instance.save()
                                        else:
                                            createCommercial(c['value'])
                                    else:
                                        commercial_instance = Commercials.objects.filter(id = c['id']).first()
                                        if c['value'] == commercial_instance.commercials:
                                            pass
                                        else:
                                            if commercial_value_instance:
                                                commercial_value_instance.visibility = True
                                                commercial_value_instance.save()
                                                commercial_instance.visibility = False
                                                commercial_instance.save()
                                            else:
                                                commercial_instance.visibility = False
                                                commercial_instance.save()
                                                createCommercial(c['value'])

                            return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
                        else:
                            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'invalid request', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized for this action',[])
        except ValidationError as e:
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong',[e.detail])

class ArchiveServices(GenericAPIView):
    serializer_class = CreateSegmentSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, type, id):
        try:
            if roleCheck(request.user,'super_admin') or request.user.is_admin:
                if type == 'segment':
                    try:
                        segment = Segment.objects.filter(visibility=False)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'segment not found', [])
                    segment = segment.first()
                    segment.visibility = False
                    segment.save()
                    return resFun(status.HTTP_200_OK, 'segment archived', [])
                elif type == 'service':
                    try:
                        service = Service.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'service not found', [])
                    service = service.first()
                    service.visibility = False
                    service.save()
                    return resFun(status.HTTP_200_OK, 'service archived', [])
                elif type == 'marketplace':
                    try:
                        marketplace = Marketplace.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'marketplace not found', [])
                    marketplace = marketplace.first()
                    marketplace.visibility = False
                    marketplace.save()
                    return resFun(status.HTTP_200_OK, 'marketplace archived', [])
                elif type == 'program':
                    try:
                        program = Program.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'program not found', [])
                    program = program.first()
                    program.visibility = False
                    program.save()
                    return resFun(status.HTTP_200_OK, 'program archived', [])

                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'invalid request', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized for this action',[])
        except ValidationError as e:
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong',[e.detail])

class RestoreServices(GenericAPIView):
    serializer_class = CreateSegmentSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, type, id):
        try:
            if roleCheck(request.user,'super_admin') or request.user.is_admin:
                if type == 'segment':
                    try:
                        segment = Segment.objects.filter(visibility=False)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'segment not found', [])
                    segment = segment.first()
                    segment.visibility = True
                    segment.save()
                    return resFun(status.HTTP_200_OK, 'segment archived', [])
                elif type == 'service':
                    try:
                        service = Service.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'service not found', [])
                    service = service.first()
                    service.visibility = True
                    service.save()
                    return resFun(status.HTTP_200_OK, 'service archived', [])
                elif type == 'marketplace':
                    try:
                        marketplace = Marketplace.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'marketplace not found', [])
                    marketplace = marketplace.first()
                    marketplace.visibility = True
                    marketplace.save()
                    return resFun(status.HTTP_200_OK, 'marketplace archived', [])
                elif type == 'program':
                    try:
                        program = Program.objects.filter(id=id)
                    except:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'program not found', [])
                    program = program.first()
                    program.visibility = True
                    program.save()
                    return resFun(status.HTTP_200_OK, 'program archived', [])

                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'invalid request', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized for this action',[])
        except ValidationError as e:
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong',[e.detail])

