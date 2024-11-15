from django.db import models

# Create your models here.


class ClientTurnover(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')
  def __str__(self): return str(self.title)

class BusinessType(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')

class BusinessCategory(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')
  def __str__(self): return (self.title)

class FirmType(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')

class ContactPreference(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')

class PaymentModel(models.Model):
  type = models.CharField(max_length=100, blank=True, default='')
  def __str__(self): return str(self.type)

class PaymentTerms(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')
  def __str__(self): return str(self.title)

class PaidBy(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')
  def __str__(self): return str(self.title)

class LeadStatus(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')
  def __str__(self): return str(self.title)

class CountryCode(models.Model):
  name = models.CharField(max_length=100)
  dial_code = models.CharField(max_length=50)
  code = models.CharField(max_length=10)
  def __str__(self): return str(self.name)

class ClientDesignation(models.Model):
  title = models.CharField(max_length=100, blank=True, default='')
  def __str__(self): return str(self.title)


class ApprovalType(models.Model):
  title = models.CharField(max_length=50)

class ActionType(models.Model):
  title = models.CharField(max_length=500, blank=True, default='')


class NotInterested(models.Model):
    title = models.CharField(max_length=500, blank=True, default='')
    def __str__ (self): return self.title


class Unresponsive(models.Model):
    title = models.CharField(max_length=500, blank=True, default='')
    def __str__ (self): return self.title


class ApprovalStatus(models.Model):
    title = models.CharField(max_length=50)
    def __str__ (self): return self.title