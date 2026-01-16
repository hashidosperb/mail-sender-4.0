
from re import T
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import api_view, permission_classes

from account.models import Clients,ContactFormMessages,CustomMessages, Message, SmsClient, SmsTemplate
from main.functions import get_latest_id
from rest_framework.parsers import JSONParser,FormParser, MultiPartParser,FileUploadParser
from rest_framework.decorators import parser_classes

from erp.settings import DEFAULT_FROM_EMAIL
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import urllib.request
import urllib.parse
import json
import requests


@api_view(['POST',])
@permission_classes([])
@parser_classes([JSONParser,FormParser, MultiPartParser,FileUploadParser])
def send_view(request,pk):
    if request.method == 'POST':
        data = {}
        name = request.data.get('enq_name')
        phone = request.data.get('enq_phone')
        email = request.data.get('enq_email', '0').lower()
        message = request.data.get('enq_message')
        company = Clients.objects.get(pk=pk)
        company_domain = company.domain
        company_email = company.email
        from_email = company_domain + "<" + DEFAULT_FROM_EMAIL + ">"

        try:
            sub = "Mail From :" + company_domain
            subject = "Mail From :" + company_domain
            html_context = {
                "domain" : company_domain,
                "name" : name,
                "phone" : phone,
                "email" : email,
                "message" : message,
            }
            html_content = render_to_string('email_templates/contact_form_mail.html', html_context)
            plain_message = "Name: " + name + "\n Phone: " + phone + "\n Email: " + email + "\n Message: " + message 
            try:
                msg = EmailMultiAlternatives(subject, plain_message, from_email, [company_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                msg_id = get_latest_id(ContactFormMessages)
                ContactFormMessages.objects.create(
                    client=company,
                    id=msg_id,
                    name = name,
                    email = email,
                    phone = phone,
                    message = message,
                )
                data['response'] = 'Mail Sent'
                data['status'] = 'true'
                return Response(data,status = status.HTTP_200_OK)
            except:
                data['response'] = 'Somthing Wrong !'
                data['status'] = 'false'
                return Response(data,status = status.HTTP_400_BAD_REQUEST)
        except:
            data['response'] = 'Somthing Wrong'
            data['status'] = 'false'
            return Response(data,status = status.HTTP_400_BAD_REQUEST)



@api_view(['POST',])
@permission_classes([])
@parser_classes([JSONParser,FormParser, MultiPartParser,FileUploadParser])
def custom_mail_view(request,pk):
    if request.method == 'POST':
        data = {}
        to_email = request.data.get('to_email')
        subject = request.data.get('subject')
        html_data = request.data.get('html_data')
        company = Clients.objects.get(pk=pk)
        company_domain = company.domain
        from_email = company_domain + "<" + DEFAULT_FROM_EMAIL + ">"
        try:
            try:
                msg = EmailMultiAlternatives(subject, html_data, from_email, [to_email])
                msg.attach_alternative(html_data, "text/html")
                msg.send()
                data['response'] = 'Mail Sent'
                data['status'] = 'true'
                msg_id = get_latest_id(CustomMessages)
                CustomMessages.objects.create(
                    client=company,
                    id=msg_id,
                    to_email = to_email,
                    subject = subject,
                    html_data = html_data,
                )
                return Response(data,status = status.HTTP_200_OK)
            except Exception as e:
                # print(e)
                data['response'] = 'Somthing Wrong !'
                data['status'] = 'false'
                return Response(data,status = status.HTTP_400_BAD_REQUEST)
        except:
            data['response'] = 'Somthing Wrong'
            data['status'] = 'false'
            return Response(data,status = status.HTTP_400_BAD_REQUEST)


@api_view(['POST',])
@permission_classes([])
@parser_classes([JSONParser,FormParser, MultiPartParser,FileUploadParser])
def send_sms_view(request,client_pk,template_pk=None):
    if request.method == 'POST':
        data = {}
        message = request.data.get('message')
        numbers = request.data.get('phone')
        sender = request.data.get('sender')
        status_code = status.HTTP_200_OK 
        data = processSMS(client_pk,numbers, sender, message)
    return Response(data,status = status_code)



@api_view(['POST',])
@permission_classes([])
@parser_classes([JSONParser,FormParser, MultiPartParser,FileUploadParser])
def send_sms_otp(request,client_pk):
    if request.method == 'POST':
        otp = request.data.get('otp')
        numbers = request.data.get('phone')
        sender = request.data.get('sender', 'OSPERB')
        template = request.data.get('template', 1)
        message = "Your OTP is : {}\nnOSPERB INNOVATIONS".format(otp)
        status_code = status.HTTP_400_BAD_REQUEST

        if(template==1):
            message = "Your OTP is : {}\n\nOSPERB INNOVATIONS".format(otp)
            data = processTextlocalOTP(client_pk,numbers, sender, message)
        elif(template==2):
            data = processFast2SmsOtp(client_pk,numbers, otp,"176537","OSPERB")

        elif(template==3):
            data = processFast2SmsOtp(client_pk,numbers, otp,"176535","OSPERB")

        elif(template==4):
            message = "{} is your OTP\n\nOSPERB INNOVATIONS".format(otp)
            data = processTextlocalOTP(client_pk,numbers, sender, message)
        elif(template==5):
            data = process2factorOTP(client_pk,numbers, otp)
        else:
            message = "{} is the OTP to access the app.\n\nsent via OSPERB".format(otp)
            data = processTextlocalOTP(client_pk,numbers, sender, message)
        
        if(data['response'] == 'Success'):
            status_code = status.HTTP_200_OK
    return Response(data,status = status_code)


def processSMS(client_pk,numbers, sender, message):
    data = {}
    try:
        sms_client = SmsClient.objects.get(pk=client_pk)
        balance = sms_client.balance
        if((sms_client.payment_type=="prepaid" and balance > 0) or (sms_client.payment_type=="postpaid")):
            sms = json.loads(sendTextlocalSMS(numbers, sender, message))
            data['sms_response'] = sms
            if(("status" in sms and sms["status"] == "success") or (sms["message"][0]=="SMS sent successfully.")):
                if('balance' in data['sms_response']):
                    del data['sms_response']['balance']
                    cost = sms["cost"]
                else:
                    cost = 40
                sms_client.unpaid_sms += cost
                sms_client.total_sms += cost
                sms_client.balance -= cost
                # sms_template = SmsTemplate.objects.get(pk=template_pk)
                # sms_client.pending_payment += int(sms_template.sms_charge)
                sms_client.save()
                message = Message.objects.create(
                    # template = sms_template,
                    sms_client = sms_client,
                    cost = cost,
                    phone = numbers,
                    sender = sender,
                    message = message
                )
                if(balance >= 50 > sms_client.balance):
                    sendBalanceAlert(sms_client)

                data['response'] = 'Success'
                data['status'] = 'true'
                data['balance'] = sms_client.balance 
        
            else:
                data['response'] = 'Failed'
                data['status'] = 'false'
                data['balance'] = sms_client.balance 

        else:
            data['response'] = 'Insufficient credits'
            data['status'] = 'false'
    except Exception as e:
        data['response'] = 'Something Wrong'
        data['status'] = 'false'
        print(e)
    return data


def processTextlocalOTP(client_pk,numbers, sender, message):
    data = {}
    try:
        sms_client = SmsClient.objects.get(pk=client_pk)
        balance = sms_client.balance
        if((sms_client.payment_type=="prepaid" and balance > 0) or (sms_client.payment_type=="postpaid")):
            sms = json.loads(sendTextlocalSMS(numbers, sender, message))
            data['sms_response'] = sms
            if(sms["status"] == "success"):
                del data['sms_response']['balance']
                cost = sms["cost"]
                sms_client.unpaid_sms += cost
                sms_client.total_sms += cost
                sms_client.balance -= cost
                # sms_template = SmsTemplate.objects.get(pk=template_pk)
                # sms_client.pending_payment += int(sms_template.sms_charge)
                sms_client.save()
                message = Message.objects.create(
                    # template = sms_template,
                    sms_client = sms_client,
                    cost = cost,
                    phone = numbers,
                    sender = sender,
                    message = message
                )
                if(balance >= 50 > sms_client.balance):
                    sendBalanceAlert(sms_client)

                data['response'] = 'Success'
                data['status'] = 'true'
                data['balance'] = sms_client.balance 
        
            else:
                data['response'] = 'Failed'
                data['status'] = 'false'
                data['balance'] = sms_client.balance 

        else:
            data['response'] = 'Insufficient credits'
            data['status'] = 'false'
    except Exception as e:
        data['response'] = 'Something Wrong'
        data['status'] = 'false'
        print(e)
    return data


def processFast2SmsOtp(client_pk,numbers, otp,message_id,sender_id):
    data = {}
    try:
        sms_client = SmsClient.objects.get(pk=client_pk)
        balance = sms_client.balance
        if((sms_client.payment_type=="prepaid" and balance > 0) or (sms_client.payment_type=="postpaid")):
            sms = json.loads(sendFast2SmsOtp(numbers, otp,message_id,sender_id))
            data['sms_response'] = sms
            if(sms["message"][0]=="SMS sent successfully."):
                cost = 40
                sms_client.unpaid_sms += cost
                sms_client.total_sms += cost
                sms_client.balance -= cost
                # sms_template = SmsTemplate.objects.get(pk=template_pk)
                # sms_client.pending_payment += int(sms_template.sms_charge)
                sms_client.save()
                message = Message.objects.create(
                    sms_client = sms_client,
                    cost = cost,
                    phone = numbers,
                    sender = "fast2sms",
                    message = "message_id:{},otp:{}".format(message_id,otp) 
                )
                if(balance >= 50 > sms_client.balance):
                    sendBalanceAlert(sms_client)

                data['response'] = 'Success'
                data['status'] = 'true'
                data['balance'] = sms_client.balance 
        
            else:
                data['response'] = 'Failed'
                data['status'] = 'false'
                data['balance'] = sms_client.balance 

        else:
            data['response'] = 'Insufficient credits'
            data['status'] = 'false'
    except Exception as e:
        data['response'] = 'Something Wrong'
        data['status'] = 'false'
        print(e)
    return data




def process2factorOTP(client_pk,numbers, otp):
    data = {}
    try:
        sms_client = SmsClient.objects.get(pk=client_pk)
        balance = sms_client.balance
        if((sms_client.payment_type=="prepaid" and balance > 0) or (sms_client.payment_type=="postpaid")):
            sms = send2factorOTP(numbers, otp)
            data['sms_response'] = sms
            if(sms["Status"] == "success"):
                del data['sms_response']['balance']
                cost = sms["cost"]
                sms_client.unpaid_sms += cost
                sms_client.total_sms += cost
                sms_client.balance -= cost
                # sms_template = SmsTemplate.objects.get(pk=template_pk)
                # sms_client.pending_payment += int(sms_template.sms_charge)
                sms_client.save()
                message = Message.objects.create(
                    # template = sms_template,
                    sms_client = sms_client,
                    cost = cost,
                    phone = numbers,
                    sender = "2factor",
                    message = message
                )
                if(balance >= 50 > sms_client.balance):
                    sendBalanceAlert(sms_client)

                data['response'] = 'Success'
                data['status'] = 'true'
                data['balance'] = sms_client.balance 
        
            else:
                data['response'] = 'Failed'
                data['status'] = 'false'
                data['balance'] = sms_client.balance 

        else:
            data['response'] = 'Insufficient credits'
            data['status'] = 'false'
    except Exception as e:
        data['response'] = 'Something Wrong'
        data['status'] = 'false'
        print(e)
    return data

# def sendTextLocalSMS(apikey, numbers, sender, message,):
#     msg_array =message.split("is the OTP to access") 
#     if(len(msg_array)>=2):
#         otp = msg_array[0].replace(" ","")
#         otp = msg_array[0].replace("\n","")
#         numbers = numbers.replace("91","")
#         x = requests.get("https://www.fast2sms.com/dev/bulkV2?authorization=MPpFvZbcQnf8UR2Ad9eY4W3qLGSIjBtHkiCxDmNrEaw7Xosyhg3Y5Q4TNVLpUG7KnHzAWiMIhSjXd8Js&route=otp&variables_values=" + otp + "&flash=0&numbers=" + str(numbers))
#         return x.json()
 
#     else:
#         data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
#             'message' : message, 'sender': sender,})
#         data = data.encode('utf-8')
#         request = urllib.request.Request("https://api.textlocal.in/send/?")
#         f = urllib.request.urlopen(request, data)
#         fr = f.read()
#         print(fr)
#         return(fr)
    
def sendTextlocalSMS(numbers, sender, message,):
    message = message.replace("Please do not share this with anyone","sent via OSPERB") 
    otp_message = message.split(" is the OTP")    
    if(len(otp_message)>1):
        #message = "your otp is : {}\n\n-sent via OSPERB".format(otp_message[0])
        # message = "{} is the OTP to access the app.\n\nsent via OSPERB".format(otp_message[0])
        message = "Your OTP is : {}\n\nOSPERB INNOVATIONS".format(otp_message[0])
        res = sendFast2SmsOtp(numbers, otp_message[0],"176537","OSPERB")
        
        
    else:
        data =  urllib.parse.urlencode({'apikey': "MzU0YjZiNjI1MzMwNjQ2MzQ2NzQ2MzU5NDQzMjc4NDQ=", 'numbers': numbers,
            'message' : message, 'sender': sender,})
        data = data.encode('utf-8')
        request = urllib.request.Request("https://api.textlocal.in/send/?")
        f = urllib.request.urlopen(request, data)
        res = f.read()
    return(res)


def sendFast2SmsOtp(phone, otp,message,sender="OSPERB"):
    # print(type(phone))

    if(type(phone)==list):
        phone = ",".join(map(str, phone))
    if len(str(phone)) > 10:
        phone = str(phone)[2:]
    print(phone)
    api_key = "LM5PrTIfjnRNkyKzeHxA6E4sqtvQDd3ihlgwV7p9WGX8ZUBbC2CNQTia3zgLnkR2YpqfGJAmcvhw1Bu7"
    url = "https://www.fast2sms.com/dev/bulkV2?authorization={}&route=dlt&sender_id={}&message={}&variables_values={}&flash=0&numbers={}&schedule_time=".format(api_key,sender,message,otp,phone)
    payload={}
    headers = {}
    res = requests.request("GET", url, headers=headers, data=payload)
    res = json.dumps(res.json())
    return(res)



def sendTextlocalSMS2(numbers, sender, message,):
    data =  urllib.parse.urlencode({'apikey': "MzU0YjZiNjI1MzMwNjQ2MzQ2NzQ2MzU5NDQzMjc4NDQ=", 'numbers': numbers,
        'message' : message, 'sender': sender,})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)

def send2factorOTP(phone, otp):
    api_key = "a11eca91-127c-11ef-8b60-0200cd936042"
    url = "https://2factor.in/API/V1/{}/SMS/{}/{}/OTP1".format(api_key,phone,otp)
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return(response.json())




def sendBalanceAlert(sms_client):
    subject = "Alert: Low SMS Credits"
    html_data = """
    Dear <b>{}</b>,
    <br><br><br>We hope you are well. This is to notify you that your current SMS credits are running low. <b>You currently have {} credits remaining</b>.
    <br><br>To ensure uninterrupted service, we recommend replenishing your SMS credits at your earliest convenience.
    <br><br>If you have any questions or need assistance, please feel free to reach out to our support team.
    <br><br>Best regards,
    <br><br><br><b>OSPERB INNOVATIONS.</b>
    """.format(sms_client.company,sms_client.balance)
    sendMail(subject, html_data, sms_client.email,"osperb.com")


def sendMail(subject, html_data, to_email,company_domain):
    from_email = company_domain + "<" + DEFAULT_FROM_EMAIL + ">"
    try:
        msg = EmailMultiAlternatives(subject, html_data, from_email, [to_email])
        msg.attach_alternative(html_data, "text/html")
        msg.send()
    except Exception as e:
        print(e)

            
