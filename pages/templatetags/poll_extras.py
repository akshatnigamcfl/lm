from django import template
from leads.models import TurnArroundTime
from datetime import datetime
import math
from leads.models import ServiceCategory, Leads, UserAccount, Segment, Service, Marketplace, Program

register = template.Library()


def customreplacespace(a, b, *args, **kwargs):
    return a.replace(b,' ')


def getDeadline(upload_date, *args, **kwargs):
    tat = TurnArroundTime.objects.all().first()
    today = datetime.now()
    upload_date = datetime.strptime(str(upload_date),"%Y-%m-%d %H:%M:%S.%f%z")
    upload_date = upload_date.replace(tzinfo=None)
    deadline = (today - upload_date).total_seconds()
    deadline = (math.ceil((int(tat.duration) - math.floor(int(deadline // (3600)))) / 24) -1 )
    return deadline


def in_list(value, arg):
    return value in arg


def getStatus(lead_id, *args, **kwargs):
    # print('lead_id ***', lead_id)
    lead_status = ServiceCategory.objects.get(lead_id=lead_id)
    status_history = lead_status.status_history.all().order_by('-id').first()
    return status_history.status.title

def getStatusId(lead_id, *args, **kwargs):
    lead_status = ServiceCategory.objects.get(lead_id=lead_id)
    status_history = lead_status.status_history.all().order_by('-id').first()
    print(status_history)
    return status_history.status.id


def conversion_rate(closed, assigned):
    if assigned == 0:
        return 0
    return round((closed * 100) / assigned, 2)


def is_hot_lead(lead_id):
    lead_instance = Leads.objects.get(service_category_all__lead_id=lead_id)
    if lead_instance.hot_lead == True:
        return True
    else:
        return False


def role_validity(user,role):
    return user.user_role.filter(title=role).exists()

def getReportingAssociate(user):
    user = UserAccount.objects.filter(reporting_manager = user)
    return user if user.exists() else None

def getAssociate(id):
    user = UserAccount.objects.filter(id = id)
    return user.first() if user.exists() else None

def getSegment(id):
    user = Segment.objects.filter(id = id)
    return user.first() if user.exists() else None

def getService(id):
    user = Service.objects.filter(id = id)
    return user.first() if user.exists() else None

def getMarketplace(id):
    user = Marketplace.objects.filter(id = id)
    return user.first() if user.exists() else None

def getProgram(id):
    user = Program.objects.filter(id = id)
    return user.first() if user.exists() else None

def stringToList(string):
    return string.split('%2C')

# @register.simple_tag()
# def multiply(a, b, *args, **kwargs):
#     # you would need to do any localization of the result here
#     # print('qty*************8', a*b  )
#     return a*b

# register.filter('multiply',multiply)



# def substract(a, b, *args, **kwargs):
#     # you would need to do any localization of the result here
#     # print('qty*************8', a*b  )
#     return a-b

# register.filter('substract',substract)


# def loop_length_generator(a, *args, **kwargs):
#     # you would need to do any localization of the result here
#     # print('qty*************8', a*b  )
#     data = ''
#     for aa in range(a):
#         data += str(0)
#     return data


register.filter('getStatusId',getStatusId)
register.filter('getStatus',getStatus)
register.filter('in_list',in_list)
register.filter('getDeadline',getDeadline)
register.filter('customreplacespace',customreplacespace)
register.filter('conversion_rate',conversion_rate)
register.filter('is_hot_lead',is_hot_lead)
register.filter('role_validity',role_validity)
register.filter('getReportingAssociate',getReportingAssociate)
register.filter('stringToList',stringToList)
register.filter('getAssociate',getAssociate)
register.filter('getSegment',getSegment)
register.filter('getService',getService)
register.filter('getMarketplace',getMarketplace)
register.filter('getProgram',getProgram)