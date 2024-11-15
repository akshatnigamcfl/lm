from rest_framework import serializers
from account.models import *
from leads.models import *
from dropdown.models import *
from account.func import generate_random_code




class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model=UserAccount
        fields=['email','password']


class UserSerializer(serializers.Serializer):
    user_role = serializers.CharField(allow_null=True)
    name = serializers.CharField(allow_null=True)
    email = serializers.CharField(allow_null=True)


class UserRegisterFields(serializers.ModelSerializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    mobile_number = serializers.CharField()
    user_role = serializers.IntegerField()
    program = serializers.ListField(allow_null=True)

class UserRegisterAdminSerializer(UserRegisterFields):
    reporting_manager = serializers.IntegerField(allow_null=True)
    class Meta:
        model = UserAccount
        fields = [ 'name' , 'email', 'mobile_number', 'reporting_manager', 'user_role' , 'program' ]
    def save(self):
        registrationValidation(self)
        user = registrationSave(self)
        return user

class UserRegisterSerializer(UserRegisterFields):
    reporting_manager = serializers.IntegerField()
    class Meta:
        model = UserAccount
        fields = [ 'name' , 'email', 'mobile_number', 'reporting_manager', 'user_role' , 'program' ]
    def save(self):
        registrationValidation(self)
        user = registrationSave(self)
        return user
    
def registrationValidation(self):
    if self.validated_data.get('name') == None:
        raise serializers.ValidationError("name field is required")
    if self.validated_data.get('mobile_number') == None:
        raise serializers.ValidationError("mobile number field is required")

    if len(self.validated_data.get('mobile_number')) > 15 or len(self.validated_data.get('mobile_number')) < 10 :
        raise serializers.ValidationError("mobile number should be of 10 digits")
    
    print("self.validated_data.get('reporting_manager')", self.validated_data.get('reporting_manager'))

    def validateReportingManager():
        if not UserAccount.objects.filter(id=self.validated_data.get('reporting_manager').id).exists():
            raise serializers.ValidationError("invalid field reporting manager")

    if self.context['user'].is_admin:
        if not self.validated_data.get('reporting_manager') == None:
            validateReportingManager()
        else:
            pass
    else:
        if self.validated_data.get('reporting_manager') == None:
            raise serializers.ValidationError("reporting manager field is required")
        else:
            validateReportingManager()

    if self.validated_data.get('user_role') == None:
        raise serializers.ValidationError("user role field is required")
    elif not UserRole.objects.filter(id=self.validated_data.get('user_role')).exists():
        raise serializers.ValidationError("invalid field user role")
        
    if not self.validated_data.get('program') == None:
        for p in self.validated_data.get('program'):
            if not Program.objects.filter(id=p).exists():
                raise serializers.ValidationError("invalid field program")
    
def registrationSave(self):
    user = UserAccount(
        email = self.validated_data['email'].lower(),
        name = self.validated_data['name'].lower(),
        mobile_number = self.validated_data['mobile_number'],
        reporting_manager = UserAccount.objects.get(id=self.validated_data['reporting_manager'].id) if self.validated_data['reporting_manager'] != None else self.validated_data['reporting_manager'],
        user_token = generate_random_code(),
        employee_status = EmployeeStatus.objects.get(title = 'active'),
        visibility = True,
    )
    user.save()    
    return user


class getUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    role = serializers.ListField()


class ViewUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField() 
    mobile_number = serializers.CharField()
    email_id = serializers.CharField() 
    user_role = serializers.ListField() 
    employee_status = serializers.DictField()
    reporting_manager = serializers.DictField()
    program = serializers.ListField()




class UpdateUserSerializer(serializers.ModelSerializer):
    user_role = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    mobile_number = serializers.CharField()
    program = serializers.ListField(allow_null=True)
    reporting_manager = serializers.IntegerField()

    class Meta:
        model = UserAccount
        fields = ['name', 'email', 'mobile_number', 'reporting_manager', 'user_role', 'employee_status', 'program', ]

    def validate(self, data):

        # if data['reporting_manager'] == None and not self.instance.is_admin:
        #     raise serializers.ValidationError('reporting manager field is required')
        # else:

        def validateReportingManager():
            if not UserAccount.objects.filter(id=data['reporting_manager']).exists():
                raise serializers.ValidationError("invalid field reporting manager")

        if self.context['user'].is_admin:
            if not data['reporting_manager'] == None:
                validateReportingManager()
            else:
                pass
        else:
            if data['reporting_manager'] == None:
                raise serializers.ValidationError("reporting manager field is required")
            else:
                validateReportingManager()
        if data['user_role'] == None:
            raise serializers.ValidationError('user role field is required')

        if len(dict(data)) == 0:
            raise serializers.ValidationError('data is required to update')
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.email = validated_data.get('email')
        instance.mobile_number = validated_data.get('mobile_number')
        instance.reporting_manager = UserAccount.objects.get(id=validated_data.get('reporting_manager'))
        instance.employee_status = validated_data.get('employee_status')
        instance.save()
        return validated_data



class ResetFirstLoginSerializer(serializers.Serializer):
    pass