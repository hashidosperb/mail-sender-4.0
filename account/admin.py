from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import Account,Clients,ContactFormMessages,CustomMessages, Message, SmsClient, SmsTemplate


class AccountAdmin(UserAdmin):
    list_display = ('pk','username','email','date_joined', 'last_login', 'is_admin','is_staff')
    search_fields = ('pk', 'email','username')
    readonly_fields=('pk', 'date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)


class ClientsAdmin(admin.ModelAdmin):
    list_display = ('pk','company','email','domain', 'phone', 'date_updated')
admin.site.register(Clients, ClientsAdmin)

class ContactFormMessagesAdmin(admin.ModelAdmin):
    list_display = ('pk','client','name','email','phone','message', 'date_updated')
admin.site.register(ContactFormMessages, ContactFormMessagesAdmin)

class CustomMessagesAdmin(admin.ModelAdmin):
    list_display = ('pk','client','to_email','subject','html_data', 'date_updated')
admin.site.register(CustomMessages, CustomMessagesAdmin)


class SmsClientAdmin(admin.ModelAdmin):
    list_display = ('pk','company','email','domain', 'phone', 'date_updated','pending_payment','total_sms','unpaid_sms','payment_type','balance')
admin.site.register(SmsClient, SmsClientAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('pk','template','sms_client','phone','sender','message', 'date_updated')
admin.site.register(Message, MessageAdmin)

class SmsTemplateAdmin(admin.ModelAdmin):
    list_display = ('pk','template_name','template', 'date_updated')
admin.site.register(SmsTemplate, SmsTemplateAdmin)
