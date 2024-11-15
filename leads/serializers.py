from rest_framework import serializers
from leads.models import *
from account.func import getClientId, getLeadId
import re





class LeadUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    class Meta:
        # models=all_identifiers
        fields=["file"]


class CreateLeadManualSerializer(serializers.Serializer):
    client_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(max_length = 15, required=True)
    email_id = serializers.EmailField(allow_null=True, required=True)
    business_name = serializers.CharField(allow_null=True, required=False)
    brand_name = serializers.CharField(allow_null=True, required=False)
    alternate_phone_number = serializers.CharField(allow_null=True, required=False)
    alternate_email_id = serializers.EmailField(allow_null=True, required=False)
    business_category = serializers.IntegerField(allow_null=True, required=False)
    client_turnover = serializers.IntegerField(allow_null=True, required=False)
    program = serializers.ListField(required=False)
    hot_lead = serializers.BooleanField(required=False)

    def validate(self, attrs):

        client_name = attrs.get('client_name')
        phone_number = attrs.get('phone_number')
        alternate_phone_number = attrs.get('alternate_phone_number')
        email_id = attrs.get('email_id')
        alternate_email_id = attrs.get('alternate_email_id')
        business_name = attrs.get('business_name')
        brand_name = attrs.get('brand_name')
        business_category = attrs.get('business_category')
        client_turnover = attrs.get('client_turnover')
        hot_lead = attrs.get('hot_lead')
        program = attrs.get('program')

        
        duplicate_leads = []
        phone_number_list = [phone_number]
        if alternate_phone_number: phone_number_list.append(alternate_phone_number)

        for ph in phone_number_list:
            if ph != None:
                if len(ph) < 9:
                    raise serializers.ValidationError('a valid digit number is required')
                else:
                    dup_contact = Leads.objects.filter(contact_number = ph)
                    if dup_contact.exists():
                        for dup in dup_contact:
                            if dup.client_id != None:
                                duplicate_leads.append({'client_id': str(dup.client_id), 'remark': [r.remark for r in dup.remark.all()]})

                            # [str(r.remark) for r in  Remark_history.objects.filter(client_id = dup.id)]


        email_id_list = [email_id, alternate_email_id]

        if email_id:
            for em in email_id_list:
                if em != None:
                    pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
                    input_string = em
                    if pattern.match(input_string):
                        dup_email = Leads.objects.filter(email_id = em)
                        if dup_email.exists():
                            for dup in dup_email:
                                for dcl in duplicate_leads:
                                    if str(dcl['client_id']) != str(dup.client_id):
                                        print(dcl['client_id'])
                                        print(dup.client_id)
                                        duplicate_leads.append({'client_id': str(dup.client_id) , 'remarks': [r.remark for r in dup.remark.all()]})
                                        break
                                    
                                    # [str(d.remark) for d in Remark_history.objects.filter(client_id = dup.id)]         
                    else:
                        raise serializers.ValidationError(f'{em} is not a valid email address')
            
        if duplicate_leads and len(duplicate_leads) > 0:
            raise serializers.ValidationError('lead already exists with this contact number or email id')
        
        if client_turnover != None:
            client_turnover_INST = ClientTurnover.objects.filter(id = client_turnover).exists()
            if not client_turnover_INST:
                raise serializers.ValidationError('client turnover field is not valid')
            
        if business_category != None:
            business_cat_INST = BusinessCategory.objects.filter(id = business_category).exists()
            if not business_cat_INST:
                raise serializers.ValidationError('business category field is not valid')
            
        if len(program) < 1:
            raise serializers.ValidationError(f"select program to create lead")
        return attrs
    

    def create(self, validated_data):
        client_id = getClientId()
        validated_data['client_id'] = client_id

        for key in validated_data:
            if isinstance(validated_data[key] ,str):
                validated_data[key] = validated_data[key].lower()
            else :
                validated_data[key] = validated_data[key]

        v_data = {
            'client_id' : validated_data['client_id'], 
            'client_name': validated_data['client_name'],
            'contact_number': validated_data['phone_number'],
            'email_id': validated_data['email_id'] if validated_data['email_id'] else None,
            }
        
        if 'business_name' in validated_data:
            v_data['business_name'] = validated_data['business_name'] 

        if 'brand_name' in validated_data:
            v_data['brand_name'] = validated_data['brand_name']
        
        if 'alternate_contact_number' in validated_data:
            v_data['alternate_contact_number'] = validated_data['alternate_contact_number']
        if 'alternate_email_id' in validated_data:
            v_data['alternate_email_id'] = validated_data['alternate_email_id']
        if 'business_category' in validated_data:
            v_data['business_category'] = BusinessCategory.objects.filter(id = validated_data['business_category']).first()
        if 'client_turnover' in validated_data:
            v_data['client_turnover'] = ClientTurnover.objects.filter(id = validated_data['client_turnover']).first()
        if 'hot_lead' in validated_data:
            v_data['hot_lead'] = validated_data['hot_lead']
            
        data = Leads.objects.create(**v_data)

        return data




class UpdateLeadSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(max_length=100)
    email_id = serializers.EmailField()
    contact_number = serializers.CharField(max_length=15)
    business_name = serializers.CharField(max_length=100, allow_null=True, required=False)
    gst = serializers.CharField(max_length=100, allow_null=True, required=False)
    seller_address = serializers.CharField(max_length=500, allow_null=True, required=False)
    brand_name = serializers.CharField(max_length=100, allow_null=True, required=False)
    business_category = serializers.IntegerField(allow_null=True, required=False)
    client_turnover = serializers.IntegerField(allow_null=True, required=False)
    associate = serializers.IntegerField()
    status = serializers.IntegerField()
    program = serializers.ListField()
    commercial_id = serializers.IntegerField(required=False)
    lead_id = serializers.CharField()
    client_designation = serializers.IntegerField( allow_null=True, required=False)

    class Meta:
        model = Leads
        fields = ['client_name', 'email_id', 'contact_number', 'business_name', 'gst', 'seller_address', 'business_category', 'client_turnover','associate', 'status', 'brand_name', 'program', 'lead_id', 'client_designation', 'commercial_id']

    def validate(self, attrs):

        data = serializer_validation(self,attrs, 'admin')
        return data

def serializer_validation(self, attrs, method):
        data = {}

        if attrs.get('client_name'):
            data['client_name'] = attrs.get('client_name')
        if attrs.get('email_id'):
            data['email_id'] = attrs.get('email_id')
        if attrs.get('contact_number'):
            print("attrs.get('contact_number')", attrs.get('contact_number'))
            if attrs.get('contact_number') and len(attrs.get('contact_number')) < 9:
                raise serializers.ValidationError('contact number is not valid')
            data['contact_number'] = attrs.get('contact_number')

        if attrs.get('business_name') and attrs.get('gst') != None:
            data['business_name'] = attrs.get('business_name')

        if attrs.get('gst') and attrs.get('gst') != None:
            data['gst'] = attrs.get('gst')
            
        if attrs.get('seller_address') and attrs.get('seller_address') != None :
            data['seller_address'] = attrs.get('seller_address')

        if attrs.get('brand_name'):
            data['brand_name'] = attrs.get('brand_name')

        if attrs.get('business_category'):
            # print("attrs.get('business_category')", attrs.get('business_category'))
            if not BusinessCategory.objects.get(id=attrs.get('business_category')):
                raise serializers.ValidationError('business category id is not valid')
            data['business_category'] = BusinessCategory.objects.get(id=attrs.get('business_category'))

        if attrs.get('client_turnover'):
            if not ClientTurnover.objects.get(id=attrs.get('client_turnover')):
                raise serializers.ValidationError('business category id is not valid')
            data['client_turnover'] = ClientTurnover.objects.get(id=attrs.get('client_turnover'))

        if not attrs.get('lead_id'):
            raise serializers.ValidationError('lead id is a required field')
        elif ServiceCategory.objects.filter(lead_id=attrs.get('lead_id')).exists():
            data['lead_id'] = attrs.get('lead_id')
        

        # if method == 'tm' or method == 'tl':
        if attrs.get('commercial_id'):
            if not Commercials.objects.get(id=attrs.get('commercial_id')):
                raise serializers.ValidationError('commercial id id is not valid')
            data['commercial_id'] = Commercials.objects.get(id=attrs.get('commercial_id'))


        if attrs.get('client_designation') or attrs.get('client_designation') == 0 :
            if not ClientDesignation.objects.get(id=attrs.get('client_designation')):
                raise serializers.ValidationError('client designation id is not valid')
            data['client_designation'] = ClientDesignation.objects.get(id=attrs.get('client_designation'))

        if attrs.get('associate'):
            if not UserAccount.objects.get(id=attrs.get('associate')):
                raise serializers.ValidationError('associate id is not valid')
            data['associate'] = UserAccount.objects.get(id=attrs.get('associate'))
        if attrs.get('program'):
            for p in attrs.get('program'):
                if not Program.objects.get(id=p):
                    raise serializers.ValidationError('program id is not valid')
            data['associate'] = UserAccount.objects.get(id=attrs.get('associate'))
        return data

class ApproveCommercialSerializer(serializers.Serializer):
    lead_id = serializers.CharField()

class RejectCommercialSerializer(serializers.Serializer):
    lead_id = serializers.CharField()







class ServiceCreateActiveCommercialSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class CreateSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ['segment']

    def validate(self, data):
        data['segment'] = data['segment'].lower()

        if not data['segment'] or data['segment'] == None or data['segment'] == '':
            raise serializers.ValidationError('segment is a required field')
        return data

    def create(self, validated_data):
        print('validated_data',validated_data)
        segment = Segment.objects.create(**validated_data)
        return segment
    

class CreateServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['segment','service']

    def validate(self, data):
        data['service'] = data['service'].lower()

        if not data['service'] or data['service'] == None or data['service'] == '':
            raise serializers.ValidationError('service is a required field')
        return data

    def create(self, validated_data):
        print('validated_data',validated_data)
        service = Service.objects.create(**validated_data)
        return service
    

class CreateMarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplace
        fields = ['service','marketplace']

    def validate(self, data):
        data['marketplace'] = data['marketplace'].lower()

        if not data['marketplace'] or data['marketplace'] == None or data['marketplace'] == '':
            raise serializers.ValidationError('marketplace is a required field')
        return data

    def create(self, validated_data):
        marketplace = Marketplace.objects.create(**validated_data)
        return marketplace
    


class CreateProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['marketplace','program', 'paid_by', 'payment_terms', 'comments', 'mou_required', 'service_validity']

    def validate(self, data):
        data['program'] = data['program'].lower()

        if not data['program'] or data['program'] == None or data['program'] == '':
            raise serializers.ValidationError('program is a required field')
        return data

    def create(self, validated_data):
        program = Program.objects.create(**validated_data)
        return program
    

class ViewSegmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Segment
        fields = '__all__'
    

class ViewServiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Service
        fields = '__all__'


class ViewMarketplaceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Marketplace
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    service_validity = serializers.IntegerField(allow_null=True)
    class Meta:
        model = Program
        exclude = ['commercials']


class ViewAllServiceSerializer(serializers.Serializer):
    lead_id = serializers.CharField()
    segment = serializers.DictField()
    service = serializers.DictField()
    marketplace = serializers.DictField()
    program = serializers.DictField()
    associate = serializers.DictField()
    assigned_status = serializers.CharField()
    payment_approval = serializers.CharField()
    commercial_approval = serializers.DictField()
    commercial = serializers.CharField()
    status = serializers.CharField()
    follow_up = serializers.ListField()

class LeadVisibilitySerializer(serializers.ModelSerializer):
    pass


class AddServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['lead_id','service']

class LeadStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['status_history']



class LeadHIstorySerializer(serializers.ModelSerializer):
    action_type = serializers.CharField(allow_null=True)
    date = serializers.CharField()
    updated_by = serializers.CharField()
    class Meta:
        model = LeadHistory
        fields = '__all__'

class AddSubscriptionDurationSerializer(serializers.Serializer):
    subscription_start_date = serializers.DateField()
    subscription_end_date = serializers.DateField()

class SubmitServiceAssociateSerializer(serializers.Serializer):
    pass


class CreateFollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowupHistory
        exclude = ['created_by']

class AskForDetailEmailSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    

class PreviewMouSerializer(serializers.Serializer):
    pass

class EmailMouSerializer(serializers.Serializer):
    pass

class UploadMouApprovalSerializer(serializers.Serializer):
    pass

class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    class Meta:
        fields=["file"]

class ApprovalSerializer(serializers.Serializer):
    title = serializers.CharField()

class ReasonSubmitSerializer(serializers.Serializer):
    status_id = serializers.IntegerField()
    client_id = serializers.IntegerField()
    lead_id = serializers.CharField()


class LeadsSerializer(serializers.Serializer):
    id = serializers.CharField()
    client_id = serializers.CharField()
    client_name = serializers.CharField()
    contact_number = serializers.CharField()
    alternate_contact_number = serializers.CharField()
    email_id = serializers.EmailField()
    alternate_email_id = serializers.CharField()
    upload_date = serializers.DateTimeField()
    deadline = serializers.CharField()
    services = serializers.ListField()
    service_category = serializers.ListField()
    client_turnover = serializers.IntegerField(allow_null=True)
    business_name = serializers.CharField()
    business_type = serializers.CharField()
    business_category = serializers.IntegerField(allow_null=True)
    firm_type = serializers.CharField()
    contact_preferences = serializers.CharField()
    hot_lead = serializers.BooleanField()
    gst = serializers.CharField()
    seller_address = serializers.CharField()
    request_id = serializers.CharField()
    provider_id = serializers.CharField()
    requester_id = serializers.CharField()
    requester_location = serializers.CharField()
    requester_sell_in_country = serializers.CharField()
    service_requester_type = serializers.CharField()
    lead_owner = serializers.CharField()



class StatusSerializer(serializers.Serializer):
    action_type = serializers.CharField()
    date = serializers.CharField()
    title = serializers.CharField()
    status = serializers.CharField()
    updated_by = serializers.CharField()

class FollowupSerializer(serializers.Serializer):
    action_type = serializers.CharField()
    title = serializers.CharField()
    date = serializers.CharField()
    followup_date = serializers.CharField()
    followup_time = serializers.CharField()
    notes = serializers.CharField()
    updated_by = serializers.CharField()


class AssignAssociateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['associate']


class EmailProposalSerializer(serializers.ModelSerializer):
    pass


    # class Meta:
    #     model = ServiceCategory
    #     fields = ['pricing']
class BulkActionSerializer(serializers.ModelSerializer):
    pass