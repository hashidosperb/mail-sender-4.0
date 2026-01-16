from re import template
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
import uuid

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
class Account(AbstractBaseUser):
    username = models.CharField(max_length=60, unique=True)
    email = models.EmailField(verbose_name="email", max_length=60,unique=True)
    first_name = models.CharField(max_length=30,)
    last_name = models.CharField(max_length=30,)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',]

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    def has_perm(self,perm,obj=None):
        return self.is_admin
        
    def has_module_perms(self,app_label):
        return True
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)    


class Clients(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.CharField(max_length=40,)
    email = models.CharField(max_length=70,)
    domain = models.CharField(max_length=70,)
    phone = models.CharField(max_length=20,)
    date_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clients'
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ('-date_updated',)

    def __str__(self):
        return (self.domain)

class ContactFormMessages(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    name = models.CharField(max_length=40,)
    email = models.CharField(max_length=70,)
    phone = models.CharField(max_length=20,)
    message = models.CharField(max_length=200,)
    date_updated = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'contact_form_messages'
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ('-date_updated',)

    def __str__(self):
        return (self.name + self.client.domain)

class CustomMessages(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    to_email = models.CharField(max_length=40,)
    subject = models.CharField(max_length=70,)
    html_data = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'custom_messages'
        verbose_name = _('Custom Message')
        verbose_name_plural = _('Custom Messages')
        ordering = ('-date_updated',)

    def __str__(self):
        return (self.client.domain + self.to_email)

class SmsClient(models.Model):
    PAYMENT_TYPE = (
        ('postpaid','postpaid'),
        ('prepaid','prepaid')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.CharField(max_length=40,)
    email = models.CharField(max_length=70,)
    domain = models.CharField(max_length=70,)
    phone = models.CharField(max_length=20,)
    pending_payment = models.PositiveIntegerField(default=0)
    total_sms = models.PositiveIntegerField(default=0)
    unpaid_sms = models.PositiveIntegerField(default=0)
    balance = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=9,choices=PAYMENT_TYPE,null=False,blank=False,default="postpaid")
    class Meta:
        db_table = 'sms_clients'
        verbose_name = _('Sms Client')
        verbose_name_plural = _('sms_Clients')
        ordering = ('-date_updated',)

    def __str__(self):
        return (self.domain)

class SmsTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template_name = models.CharField(max_length=128)
    template = models.TextField()
    sms_charge = models.CharField(max_length=128,default=40)
    date_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sms_templates'
        verbose_name = _('Sms template')
        verbose_name_plural = _('sms_templates')
        ordering = ('-date_updated',)

    def __str__(self):
        return (self.template_name)

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(SmsTemplate, on_delete=models.CASCADE,null=True,blank=True)
    sms_client = models.ForeignKey(SmsClient, on_delete=models.CASCADE)
    phone = models.CharField(max_length=128)
    sender = models.CharField(max_length=8)
    message = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True)
    cost = models.IntegerField(default=0)

    class Meta:
        db_table = 'message'
        verbose_name = _('Message')
        verbose_name_plural = _('messages')
        ordering = ('-date_updated',)

    def __str__(self):
        return (self.phone)