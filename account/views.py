from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
# from .func import get_tokens_for_user
# from .func import user_VF
from django.contrib.auth import authenticate
import string
import secrets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from account.models import *
from .serializers import UserSerializer
from .serializers import *
from django.core.mail import EmailMultiAlternatives
from rest_framework.exceptions import ValidationError
import math
from account.func import roleCheck
from django.contrib.auth.hashers import make_password



def generate_random_code(length=25):
    alphabet = string.ascii_letters + string.digits
    random_code = ''.join(secrets.choice(alphabet) for _ in range(length))
    return random_code

def resFun(status,message,data):
    res = Response()
    res.status_code = status
    res.data = {
        'status': status,
        'message': message,
        'data': data,
    }
    return res

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def user_VF(user):

    user_f = UserAccount.objects.filter(id=user.id)
    print('user_f', user_f )


    data = {
        # 'program' : user.program.program if user and user.program and user.program.program != '' else '-',
        'name' : user.name if user.name else None ,
        'email' : user.email if user.email else None,
        'user_role': user.user_role.first().title if user.user_role.exists() else None
    }
    
    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return  {'user': serializer.data}

class IgnoreBearerTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer'):
                return None
        return super().authenticate(request)



class Login(GenericAPIView):
    authentication_classes = [IgnoreBearerTokenAuthentication]
    serializer_class = LoginSerializer
    def post(self,request,format=None):
        try:
            serializer=LoginSerializer(data=request.data)
            if serializer:
                if serializer.is_valid(raise_exception=True):
                    email=serializer.data.get('email')  
                    password=serializer.data.get('password')
                    try:
                        UserAccount.objects.get(email=email, visibility=True)
                    except:
                        return resFun(status.HTTP_404_NOT_FOUND, 'no user account with this email id', [])
                    
                    user=authenticate(email=email,password=password)
                    if user is not None:
                        if user.visibility:
                            token=get_tokens_for_user(user)

                            return resFun(status.HTTP_200_OK, "registration successful", {'user_details': user_VF(user),"token": token})
                        else:
                            return resFun(status.HTTP_400_BAD_REQUEST, 'user is inactive, please contact administrator', [])
                    else:
                            return resFun(status.HTTP_404_NOT_FOUND, 'Email or password is not Valid', [])
            else:
                return resFun(status.HTTP_404_NOT_FOUND, 'login failed', [serializer.errors])
        except:    
            return resFun(status.HTTP_404_NOT_FOUND, 'request failed', [])


class Register(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserRegisterSerializer
    def post(self, request, format=None, *args, **kwargs):
        
        try:
            existing_user  = UserAccount.objects.filter(email = request.data.get('email').lower() if request.data.get('email') else '' )
            if existing_user.exists():
                return resFun(status.HTTP_400_BAD_REQUEST, 'user already registered with this email, please contact admin', [])
            existing_user  = UserAccount.objects.filter(mobile_number = request.data.get('mobile_number').lower() if request.data.get('mobile_number') else '' )
            if existing_user.exists():
                return resFun(status.HTTP_400_BAD_REQUEST, 'user already registered with this mobile number, please contact admin', [])
            
            if request.user.is_admin:
                serializer = UserRegisterAdminSerializer(data = request.data, context={'user': request.user})
            else:
                serializer = UserRegisterSerializer(data = request.data, context={'user': request.user})
            
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                instance.created_by = request.user
                instance.user_role.set([UserRole.objects.get(id=serializer.validated_data['user_role'])])
                if request.data.get('program'):
                    instance.program.set(request.data.get('program'))                
                instance.save()
                ua_ser = UserAccount.objects.filter(email=serializer.data['email']).first()
                message = CannedEmail.objects.get(email_type = 'welcome_email')
                message = message.email
                message = str(message).replace("{{{link}}}", f'<a href="http://localhost:8000/account/generate_password/{ua_ser.pk}/{ua_ser.user_token}">fill more details</a>')
                email_id = ua_ser.email
                subject = 'Welcome to Evitamin!'
                from_email = 'akshatnigamcfl@gmail.com'
                recipient_list = [email_id]
                text = 'email sent from MyDjango'
                email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
                email.attach_alternative(message, 'text/html')
                # email.attach_file('files/uploadFile_0dTGU7A.csv', 'text/csv')
                email.send()
                return resFun(status.HTTP_200_OK,'registration successful',serializer.data)
            else:
                return resFun(status.HTTP_400_BAD_REQUEST,'something went wrong',[serializer.errors])
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST,'request failed',[e.detail])

            
class GetUsersList(GenericAPIView):
    serializer_class = getUserSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, attribute):
        try:
            userInstance = UserAccount.objects.filter(name__icontains=attribute)
            userInstance = [{'id': u.id, 'value': u.name, 'role': [ r.title for r in u.user_role.all()] } for u in userInstance ]
            serializer = getUserSerializer(data=userInstance , many=True)
            if serializer.is_valid():
                if len(serializer.data) > 0:
                    return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
                else:
                    return resFun(status.HTTP_204_NO_CONTENT, 'no data', serializer.data)
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', serializer.errors )
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [e.detail])
        


def viewUserDictDataStructure(users):
    data = []
    for u in users:
        data.append({
            'id': u.id ,
            'name': u.name if u.name else '-', 
            'mobile_number': u.mobile_number if u.mobile_number else '-', 
            'email_id': u.email if u.email else '-', 
            'reporting_manager': { 'id': u.reporting_manager.id, 'name': u.reporting_manager.name} if u.reporting_manager else {'id': None, 'name': None} , 
            'user_role': [ {'user_role_id': ur.id, 'user_role': ur.title}  for ur in u.user_role.all()] ,
            'employee_status': {'employee_status_id': u.employee_status.id, 'employee_status': u.employee_status.title} if u.employee_status else {'employee_status_id': 0,'employee_status': ''},
            'program': [s.id for s in u.program.all() if u.program],
            })
    return data


def viewUserDict(request, page, visibility):
        limit = 10
        offset = int((page - 1) * limit)
        
        users = UserAccount.objects.filter(visibility=visibility)[offset: offset+limit]
        count = math.ceil(UserAccount.objects.filter(visibility=visibility).count() / 10)
        
        if users.exists():
            data = viewUserDictDataStructure(users)
            serializer = ViewUserSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK, 'request successful', {"data": serializer.data, 'current_page': page, 'total_pages': count})
        else:
            res = resFun(status.HTTP_204_NO_CONTENT, 'no data found', {'data': [], 'current_page': page, 'total_pages': count} )

        return res


class Users(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ViewUserSerializer
    def get(self, request, page, format=None, *args, **kwargs):
        res = viewUserDict(request, page, True)
        return res



class UserUpdate(GenericAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, id ,format=None, *args, **kwargs):

        try:
            if roleCheck(request.user,'super_admin') or roleCheck(request.user,'admin') or request.user.is_admin:
                user = UserAccount.objects.filter(id = id).first()
                
                if request.user.user_role.filter(title='admin').exists() and request.user.user_role.filter(title='user_manager').exists() :
                    if roleCheck(user,'super_admin').exists():
                        raise serializers.ValidationError('you are not authorized to make changes to this user')
                    
                if user:
                    new_data = {key: values for key, values in request.data.items() if values != '-'}
                    serializer = UpdateUserSerializer(user, data=new_data, partial=True, context={'user': request.user})
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        if request.data.get('user_role') != None :
                            user.user_role.set([UserRole.objects.get(id=serializer.validated_data['user_role'])])
                        if request.data.get('program'):
                            user.program.set(request.data.get('program'))
                        user.save()
                        return resFun(status.HTTP_200_OK, 'changes saved successfully', serializer.data )
                    else:
                        # print(serializer.errors)
                        return resFun(status.HTTP_400_BAD_REQUEST, [ f'{k} - ' + f'{v[0]}' for k, v in serializer.errors.items()] , [] )
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'invalid employee id', [] )
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized to view this data', [] )
        except ValidationError as e:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [e.detail] )



class LeaveAction(GenericAPIView):
    serializer_class = ''
    permission_classes = [IsAuthenticated]
    def post(self, request, type, leave_id ):
        try:
            try:
                employee_leave_instance = EmployeeLeaves.objects.get(id=leave_id)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid leave id', [])
            if employee_leave_instance != None:
                if type == 'approve':
                    employee_leave_instance.status = EmployeeLeaveStatus.objects.get(title='approved')
                elif type == 'reject':
                    employee_leave_instance.status = EmployeeLeaveStatus.objects.get(title='rejected')
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'invalid action type', [])                    
                employee_leave_instance.save()
                return resFun(status.HTTP_200_OK, 'request successful', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid leave id', [])
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])


class ResetFirstLogin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResetFirstLoginSerializer
    def post(self, request, user_id):
        try:
            try:
                user_instance = UserAccount.objects.get(id=user_id)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid leave id', [])

            user_instance.is_first_login = False
            user_instance.save()
            return resFun(status.HTTP_200_OK, 'request successful', [])
             
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])


class UserSearch(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ViewUserSerializer
    def get(self, request, attribute ,id, format=None, *args, **kwargs):

        if roleCheck(request.user,'super_admin')  or roleCheck(request.user,'admin') or request.user.is_admin:
            if attribute == 'name':
                name = id.replace('_',' ')
                user = UserAccount.objects.filter(name__icontains = name, visibility=True)
            # elif attribute == 'employee_id':
            #     user = UserAccount.objects.filter(employee_id__contains = id, visibility=True)
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'invalid search term', [])
                return res

            if user.exists():
                data = viewUserDictDataStructure(user)

                serializer = ViewUserSerializer(data=data, many=True)
                if serializer.is_valid(raise_exception=True):
                    res = resFun(status.HTTP_200_OK, 'request successful', serializer.data )
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [] )
            else:
                res = resFun(status.HTTP_204_NO_CONTENT, 'no user found', [] )
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized to view this data', [] )
        return res
    


def GeneratePassword(request, id, token):
    try:
        user = UserAccount.objects.get(id=id,user_token=token)
        print('user', user)
        if request.POST:
            password = request.POST.get('password')
            repeat_password = request.POST.get('repeat_password')
            if password != repeat_password:
                return render(request, 'generate_password.html', {'data': user, "error":"password & repeat password doesn't match" })
            else:
                user.user_token=generate_random_code()
                user.password = make_password(password)
                user.save()
                return render(request, 'generate_password.html', {'data': user, "success":"password updated successfully" })
            
    except ValidationError as e:
        return render(request, 'generate_password.html', {'data': 'no data', 'other_error': e.detail ,"link_error": "link is invalid or expired!" } )
    return render(request, 'generate_password.html', {'data': user})




def resetPassword(request):
    if request.POST:
        try:
            user = UserAccount.objects.get(email=request.POST.get('email'))
            message = CannedEmail.objects.get(email_type = 'reset_password')
            message = message.email
            message = str(message).replace("{{{link}}}", f'<a href="http://localhost:8000/account/generate_password/{user.pk}/{user.user_token}">Reset Password</a>')
            email_id = user.email
            subject = 'Reset Password!'
            from_email = 'akshatnigamcfl@gmail.com'
            recipient_list = [email_id]
            text = 'email sent from MyDjango'
            email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
            email.attach_alternative(message, 'text/html')
            email.send()
            return render(request, 'reset_password.html', {'data': 'no data found', "success":"email sent, please check your email to reset password!" })                
        except:
            pass
            return render(request, 'reset_password.html', {'data': 'no data found', "success":"email sent, please check your email to reset password!" })
        
    return render(request, 'reset_password.html')



