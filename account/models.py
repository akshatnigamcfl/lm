from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser)
from .func import generate_random_code
# from leads.models import Segment


class UserRole(models.Model):
    title = models.CharField(max_length=100, blank=True, default='')
    def __str__(self): return str(self.title)


class CannedEmail(models.Model):
    email = models.TextField()
    email_type = models.CharField( max_length=50, null=True, blank=True)
    def __str__(self): return str(self.email_type)


class EmployeeStatus(models.Model):
    title = models.CharField(max_length=100, blank=True, default='')
    def __str__(self): return str(self.title)


class EmployeeLeaveStatus(models.Model):
    title = models.CharField(max_length=50)


class EmployeeLeaves(models.Model):
    date_from = models.DateField()
    date_to = models.DateField()
    notes = models.CharField(max_length=300)
    status = models.ForeignKey(EmployeeLeaveStatus, on_delete=models.CASCADE)
    employee = models.ForeignKey("account.useraccount", related_name='employee_leave' ,on_delete=models.CASCADE)



class UserAccountManager(BaseUserManager):
	def create_user(self , email , password = None):
		if not email or len(email) <= 0 :
			raise ValueError("Email field is required !")
		if not password :
			raise ValueError("Password is must !")
		
		user = self.model(
			email = self.normalize_email(email) ,
		)
		user.set_password(password)
		user.save(using = self._db)
		return user
	
	def create_superuser(self , email , password):
		user = self.create_user(
			email = self.normalize_email(email),
			password = password,               
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using = self._db)
		return user
      

class UserAccount(AbstractBaseUser):
    email = models.EmailField(max_length = 200 , unique = True)
    name = models.CharField(max_length=100, null=False)
    # contact_number = models.CharField(max_length=15, null=False, blank=True)
    user_role = models.ManyToManyField(UserRole)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = True)
    is_first_login = models.BooleanField(default = True)
    employee_status = models.ForeignKey(EmployeeStatus , on_delete=models.CASCADE, default=1)
    reporting_manager = models.ForeignKey("self", related_name = 'team_leaders_of' , on_delete=models.CASCADE, null=True, blank=True)
    program = models.ManyToManyField("leads.program")
    mobile_number = models.CharField(max_length=15, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', related_name = 'creator_of', on_delete=models.CASCADE, null=True, blank=True)
    user_token = models.CharField(max_length=300, blank=True, default=generate_random_code())
    employee_leaves = models.ManyToManyField(EmployeeLeaves, related_name='user_accounts')
    visibility = models.BooleanField(default=True)
    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    def has_module_perms(self, app_label):
        return True


