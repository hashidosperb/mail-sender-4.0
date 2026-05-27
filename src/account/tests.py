from .models import SmsClient,Message

# Create your tests here.

sms_clients = SmsClient.objects.filter()


# for sms_client in sms_clients:
#     print(f"Sms Client: {sms_client.company}, Balance: {sms_client.balance}, total_sms: {sms_client.total_sms}, unpaid_sms: {sms_client.unpaid_sms}, pending_payment: {sms_client.pending_payment},payment_type: {sms_client.payment_type},")
msg = Message.objects.filter(sms_client__id="1d94d585-7b7f-4d28-adbe-ad9c6cfb3e35")

for m in msg:
    if not "Metrix360" in m.message:
        print(m.message)
        print("\n")

# print("Count : ",msg.count())
# for m in msg:
    #     print(m.id, m.sms_client, m.message, m.date_updated)


# from django.test import TestCase
# import csv
# from account.models import SmsClient, Message

# # Open a CSV file for writing
# with open('sms_clients.csv', 'w', newline='', encoding='utf-8') as csvfile:
#     writer = csv.writer(csvfile)
    
#     # Write the header row
#     writer.writerow([
#         'Company',
#         'Balance',
#         'Total SMS',
#         'Unpaid SMS',
#         'Pending Payment',
#         'Payment Type',
#         'Message Count'
#     ])
    
#     # Fetch all SMS clients and write their rows
#     sms_clients = SmsClient.objects.all()
#     for sms_client in sms_clients:
#         msg_count = Message.objects.filter(sms_client=sms_client).count()
#         writer.writerow([
#             sms_client.company,
#             sms_client.balance,
#             sms_client.total_sms,
#             sms_client.unpaid_sms,
#             sms_client.pending_payment,
#             sms_client.payment_type,
#             msg_count
#         ])

# print("CSV export completed successfully! Saved as 'sms_clients.csv'.")
