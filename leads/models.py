from django.db import models
from account.models import UserAccount
from dropdown.models import *
import json



class FollowupHistory(models.Model):
  date = models.DateField(default='0001/01/01')
  time = models.TimeField(auto_now=False, auto_now_add=False)
  notes = models.TextField()
  created_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
  created_date = models.DateTimeField(auto_now_add=True, null=True)
  def __str__(self): return str(self.date)

# class Contact_number(models.Model):
#   lead_id = models.ForeignKey("leads.Leads", on_delete=models.CASCADE, null=True, blank=None)
#   contact_number = models.CharField(max_length=100, blank=True, default='')

class Segment(models.Model):
  segment = models.CharField(max_length=100, blank=True, default='')
  visibility = models.BooleanField(default=True)
  def __str__(self): return str(self.segment)

class Service(models.Model):
  segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
  service = models.CharField(max_length=100, blank=True, default='')
  visibility = models.BooleanField(default=True)
  def __str__(self): return str(self.service)

class Marketplace(models.Model):
  service = models.ForeignKey(Service, on_delete=models.CASCADE)
  marketplace = models.CharField(max_length=100, blank=True, default='')
  visibility = models.BooleanField(default=True)
  def __str__(self): return str(self.marketplace)



class Program(models.Model):
  marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE)
  program = models.CharField(max_length=100, blank=True, default='')
  mou_required = models.BooleanField(default=True, null=True)
  paid_by = models.ForeignKey(PaidBy, on_delete=models.CASCADE, null=True)
  comments = models.CharField(max_length=100, blank=True, default='', null=True)
  payment_model = models.ForeignKey(PaymentModel, on_delete=models.CASCADE, null=True)
  payment_terms = models.ForeignKey(PaymentTerms, on_delete=models.CASCADE, null=True)
  service_validity = models.IntegerField(null=True)
  commercials = models.ManyToManyField("leads.commercials")
  visibility = models.BooleanField(default=True)
  def __str__(self): return str(self.program)



class Commercials(models.Model):
  commercials = models.CharField(max_length=100)
  lead_id = models.ManyToManyField("leads.servicecategory", related_name='lead_id_of')
  visibility = models.BooleanField(default=True)
  def __str__(self): return str(self.commercials)

class ProposalEmail(models.Model):
  program = models.ForeignKey(Program, on_delete=models.CASCADE)
  email = models.TextField()


class StatusHistory(models.Model):
  status = models.ForeignKey(LeadStatus, on_delete=models.CASCADE)
  service_category = models.ForeignKey("leads.servicecategory", on_delete=models.CASCADE , null=True)
  status_date = models.DateTimeField(auto_now=True, auto_now_add=False)
  updated_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
  def __str__(self): return str(self.status)


class Leads(models.Model):
    hot_lead = models.BooleanField(default=False)
    client_id = models.CharField(max_length=100, blank=True, default='')
    service_category = models.ManyToManyField("leads.servicecategory")
    remark = models.ManyToManyField("leads.remarkhistory")
    history = models.ManyToManyField("leads.leadhistory")
    lead_owner = models.ForeignKey("account.useraccount", on_delete=models.CASCADE, null=True, blank=True)
    
    request_id = models.CharField(max_length=100, blank=True, default='') 
    provider_id = models.CharField(max_length=100, blank=True, default='') 
    requester_id = models.CharField(max_length=100, blank=True, default='') 
    requester_location = models.CharField(max_length=100, blank=True, default='') 
    requester_sell_in_country = models.CharField(max_length=100, blank=True, default='') 
    service_requester_type = models.CharField(max_length=100, blank=True, default='') 
    marketplace = models.CharField(max_length=100, blank=True, default='') 
    current_status = models.CharField(max_length=100, blank=True, default='') 
    
    client_name = models.CharField(max_length=100, blank=True, default='') 
    contact_number = models.CharField(max_length=100, blank=True, default='') 
    alternate_contact_number = models.CharField(max_length=100, blank=True, default='')
    email_id = models.EmailField(max_length=254, null=True, blank=True, default='')
    alternate_email_id = models.EmailField(max_length=254, blank=True, default='')
    contact_preferences = models.ForeignKey(ContactPreference, on_delete=models.CASCADE, null=True, blank=True)

    business_name = models.CharField(max_length=100, null=True, blank=True, default='')
    brand_name = models.CharField(max_length=100, null=True, blank=True, default='')
    business_category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE, null=True, blank=True) 
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, null=True, blank=True)
    client_turnover = models.ForeignKey(ClientTurnover, on_delete=models.CASCADE, null=True, blank=True)
    client_designation = models.ForeignKey(ClientDesignation, on_delete=models.CASCADE, null=True, blank=True)
    gst = models.CharField(max_length=100, blank=True, default='') 
    seller_address = models.CharField(max_length=500, blank=True, default='')
    firm_type = models.ForeignKey(FirmType, on_delete=models.CASCADE, null=True, blank=True) 

    seller_website = models.CharField(max_length=100, blank=True, default='') 
    amazon_store_link = models.CharField(max_length=100, blank=True, default='') 
    facebook_store_link = models.CharField(max_length=100, blank=True, default='')
    instagram_store_link = models.CharField(max_length=100, blank=True, default='')

    created_date = models.CharField(max_length=100, blank=True, default='')
    upload_date = models.DateTimeField(auto_now_add=True, null=True)
    visibility = models.BooleanField(default=True)

    # designation_in_company = models.CharField(max_length=100, blank=True, default='')
    # name_for_mou = models.CharField(max_length=100, blank=True, default='') 
    # email_record = models.CharField(max_length=100, blank=True, default='')
    def __str__(self):return str(self.client_id)


class TurnArroundTime(models.Model):
  duration = models.IntegerField()
  def __str__(self): return str(self.duration_in_hrs)


class RemarkHistory(models.Model):
  remark = models.CharField(max_length=100, blank=True, default='')
  lead_id = models.ForeignKey( 'leads.servicecategory', on_delete=models.CASCADE, null=True, blank=True)
  def __str__(self): return str(self.remark)


class CommercialApproval(models.Model):
  commercial = models.CharField(max_length=100)
  status = models.ForeignKey("dropdown.approvalstatus", on_delete=models.CASCADE, null=True, blank=True)
  approval_type = models.ForeignKey(ApprovalType, on_delete=models.CASCADE, null=True, blank=True)
  service_category = models.ForeignKey('leads.servicecategory', on_delete=models.CASCADE, null=True, blank=True, related_name='service_category_of')
  def __str__(self): return str(self.commercial)


class JsonEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, set):
      return list(obj)
    return super().default(obj)
class JsonDecoder(json.JSONDecoder):
  def __ini__(self, *args, **kwargs):
    super().__init__(object_hook=self.custom_object_hook, *args, **kwargs)
  def custom_object_hook(self, obj):
    return obj
      

class LeadHistory(models.Model):
  action_type = models.ForeignKey(ActionType, on_delete=models.CASCADE, null=True, blank=True)
  title = models.CharField(max_length=500, blank=True, default='')
  field = models.JSONField(default=list, encoder=JsonEncoder, decoder=JsonDecoder, null=True, blank=True)
  previous = models.CharField(max_length=500, null=True, blank=True, default='')
  new = models.CharField(max_length=500, null=True, blank=True, default='')
  date = models.DateTimeField(auto_now_add=True)
  updated_by = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)


class ServiceCategory(models.Model):
  lead_id = models.CharField(max_length=100, blank=True, default='')
  program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)

  followup = models.ManyToManyField(FollowupHistory) # ForeignKey(Followup_history, on_delete=models.CASCADE, null=True, blank=True)
  status = models.ForeignKey(LeadStatus, on_delete=models.CASCADE, null=True, blank=True)
  history = models.ManyToManyField(LeadHistory)
  remark = models.ManyToManyField("leads.remarkhistory")
  payment_approval = models.ForeignKey("dropdown.approvalstatus", on_delete=models.CASCADE, null=True, blank=True)
  commercial_approval = models.ForeignKey(CommercialApproval, on_delete=models.CASCADE, null=True, blank=True)
  not_interested_reason = models.ForeignKey("dropdown.notinterested", on_delete=models.CASCADE, null=True, blank=True)
  unresponsive_reason = models.ForeignKey("dropdown.unresponsive", on_delete=models.CASCADE, null=True, blank=True)
  status_history = models.ManyToManyField(StatusHistory)
  
  associate = models.ForeignKey(UserAccount , on_delete=models.CASCADE, null=True, blank=True)
  commercials = models.ForeignKey(Commercials, related_name='commercials_of', on_delete=models.CASCADE, null=True, blank=True)
  mou = models.FileField(upload_to='mou', max_length=100, null=True, blank=True,  default='')
  payment_proof = models.FileField(upload_to='paymentproof', max_length=100, null=True, blank=True,  default='' )

  created_date = models.DateTimeField(auto_now_add=True, null=True)
  subscription_start_date = models.DateTimeField(auto_now=True, null=True)
  subscription_end_date = models.DateTimeField(auto_now=True, null=True)
  def __str__(self): return str(self.lead_id)


class EmailHistory(models.Model):
  lead_id = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=None)
  email = models.TextField()
  date = models.DateField(auto_now=False, auto_now_add=False)
  sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)