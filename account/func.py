import string
import secrets
from django.core.mail import EmailMultiAlternatives
import random
from datetime import date, datetime, timezone, timedelta
# from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
# # from account.models import UserAccount
# from .serializers import UserSerializer

# # Create your views here.

def generate_random_code(length=25):
    alphabet = string.ascii_letters + string.digits
    random_code = ''.join(secrets.choice(alphabet) for _ in range(length))
    return random_code

def roleCheck(user, role):
    return user.user_role.filter(title=role).exists()

def SendEmail(email, subject, message):
    subject = subject
    from_email = 'akshatnigamcfl@gmail.com'
    recipient_list = email
    text = 'email sent from MyDjango'
    email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
    email.attach_alternative(message, 'text/html')
    email.send()


def getLeadId():
    date = datetime.now()
    date = date.strftime('%Y%m%d%H%M%S%f')
    random_int = random.randint(100,499) + random.randint(100,499)
    lead_id = f'L{str(date) + str(random_int)}'
    return lead_id


def getClientId():
    date = datetime.now()
    date = date.strftime('%Y%m%d%H%M%S%f')
    random_int = random.randint(100,499) + random.randint(100,499)
    lead_id = f'C{str(date) + str(random_int)}'
    return lead_id


# # def resFun(status,message,data):
# #     res = Response()
# #     res.status_code = status
# #     res.data = {
# #         'status': status,
# #         'message': message,
# #         'data': data,
# #     }
# #     return res


# # def get_tokens_for_user(user):
# #     refresh = RefreshToken.for_user(user)
# #     return {
# #         'refresh': str(refresh),
# #         'access': str(refresh.access_token),
# #     }


# # def user_VF(id):
# #     user = UserAccount.objects.get(id=id)
# #     data = {
# #         'name' : user.name,
# #         'email' : user.email,
# #         'user_role': user.user_role.first().title
# #     }
# #     serializer = UserSerializer(data=data)
# #     serializer.is_valid(raise_exception=True)
# #     return  {'user': serializer.data}