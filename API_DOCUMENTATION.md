# API Documentation

This document outlines the API endpoints available in the Mail Sender application.

## Endpoints

### 1. Send Contact Mail

Sends a contact form email to the company associated with the given client ID.

*   **URL**: `/send/<pk>` OR `/send-contact-mail/<pk>/`
*   **Method**: `POST`
*   **Path Parameters**:
    *   `pk` (required): The unique identifier (ID) of the Client.

*   **Request Body (JSON/Form-Data)**:
    *   `enq_name` (string): Name of the person enquiring.
    *   `enq_phone` (string): Phone number of the person.
    *   `enq_email` (string, optional): Email of the person. Defaults to '0'.
    *   `enq_message` (string): The message content.

*   **Response**:
    *   **Success (200 OK)**:
        ```json
        {
            "response": "Mail Sent",
            "status": "true"
        }
        ```
    *   **Error (400 Bad Request)**:
        ```json
        {
            "response": "Somthing Wrong !",
            "status": "false"
        }
        ```

#### cURL Example
```bash
curl -X POST http://localhost:8000/account/api/send/1 \
     -H "Content-Type: application/json" \
     -d '{
           "enq_name": "John Doe",
           "enq_phone": "1234567890",
           "enq_email": "john@example.com",
           "enq_message": "Hello, I would like to inquire about..."
         }'
```

### 2. Send Custom Mail

Sends a custom HTML email.

*   **URL**: `/custom-mail/<pk>` OR `/send-custom-mail/<pk>/`
*   **Method**: `POST`
*   **Path Parameters**:
    *   `pk` (required): The unique identifier (ID) of the Client sending the mail.

*   **Request Body (JSON/Form-Data)**:
    *   `to_email` (string): Recipient's email address.
    *   `subject` (string): Subject of the email.
    *   `html_data` (string): HTML content of the email body.

*   **Response**:
    *   **Success (200 OK)**:
        ```json
        {
            "response": "Mail Sent",
            "status": "true"
        }
        ```
    *   **Error (400 Bad Request)**:
        ```json
        {
            "response": "Somthing Wrong !",
            "status": "false"
        }
        ```

#### cURL Example
```bash
curl -X POST http://localhost:8000/account/api/custom-mail/1 \
     -H "Content-Type: application/json" \
     -d '{
           "to_email": "recipient@example.com",
           "subject": "Special Offer",
           "html_data": "<h1>Hello!</h1><p>Check out our latest offers.</p>"
         }'
```

### 3. Send SMS

Sends an SMS message to one or more phone numbers.

*   **URL**:
    *   `/send_sms_view/<client_pk>/<template_pk>/`
    *   `/send_sms_view/<client_pk>/`
    *   `/send-sms/<client_pk>/`
*   **Method**: `POST`
*   **Path Parameters**:
    *   `client_pk` (required): The unique identifier ID of the SMS Client.
    *   `template_pk` (optional): The ID of the SMS template (if applicable).

*   **Request Body (JSON/Form-Data)**:
    *   `message` (string): The content of the SMS.
    *   `phone` (string): Phone number(s).
    *   `sender` (string): Sender ID.

*   **Response**:
    *   **Success (200 OK)**:
        ```json
        {
            "response": "Success",
            "status": "true",
            "balance": <remaining_balance>,
            "sms_response": { ... } 
        }
        ```
    *   **Error (200 OK with Failed status)**:
        ```json
        {
            "response": "Failed",
            "status": "false",
            "balance": <remaining_balance>
        }
        ```
    *   **Insufficient Credits (200 OK)**:
        ```json
        {
            "response": "Insufficient credits",
            "status": "false"
        }
        ```

#### cURL Example
```bash
curl -X POST http://localhost:8000/account/api/send-sms/1/ \
     -H "Content-Type: application/json" \
     -d '{
           "message": "Hello, this is a test message.",
           "phone": "9876543210",
           "sender": "TESTID"
         }'
```

### 4. Send SMS OTP

Sends an OTP (One Time Password) via SMS using various templates/providers.

*   **URL**: `/send-sms-otp/<client_pk>/`
*   **Method**: `POST`
*   **Path Parameters**:
    *   `client_pk` (required): The unique identifier ID of the SMS Client.

*   **Request Body (JSON/Form-Data)**:
    *   `otp` (string/number): The OTP code to send.
    *   `phone` (string): Phone number.
    *   `sender` (string, optional): Sender ID. Defaults to 'OSPERB'.
    *   `template` (integer, optional): Template selection (1-5). Defaults to 1.
        *   `1`: "Your OTP is : {otp}\n\nOSPERB INNOVATIONS" (Textlocal)
        *   `2`: Fast2Sms Service (Route 176537)
        *   `3`: Fast2Sms Service (Route 176535)
        *   `4`: "{otp} is your OTP\n\nOSPERB INNOVATIONS" (Textlocal)
        *   `5`: 2Factor OTP Service
        *   `Other`: "{otp} is the OTP to access the app.\n\nsent via OSPERB" (Textlocal)

*   **Response**:
    *   **Success (200 OK)**:
        ```json
        {
            "response": "Success",
            "status": "true",
            "balance": <remaining_balance>
        }
        ```
    *   **Error (400 Bad Request)**:
        Returned if the SMS failed to send or other errors occurred.

#### cURL Example
```bash
curl -X POST http://localhost:8000/account/api/send-sms-otp/1/ \
     -H "Content-Type: application/json" \
     -d '{
           "otp": "123456",
           "phone": "9876543210",
           "sender": "MYAPP",
           "template": 1
         }'
```
