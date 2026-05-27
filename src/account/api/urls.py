from django.urls import path
from account.api.views import(
	custom_mail_view, send_view,send_sms_view,send_sms_otp
)
app_name = 'account'

urlpatterns = [
	path('send/<pk>', send_view, name="send"),
	path('send-contact-mail/<pk>/', send_view, name="send2"),
	path('custom-mail/<pk>', custom_mail_view, name="custom_mail"),
	path('send-custom-mail/<pk>/', custom_mail_view, name="custom_mail2"),
	path('send_sms_view/<client_pk>/<template_pk>/', send_sms_view, name="send_sms_view"),
	path('send_sms_view/<client_pk>/', send_sms_view, name="send_sms_view2"),
	path('send-sms/<client_pk>/', send_sms_view, name="send_sms_view3"),
	path('send-sms-otp/<client_pk>/', send_sms_otp, name="send_sms_otp"),
]