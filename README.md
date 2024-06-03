## Inbox4us - Technical Test Requirements for Odoo Hotel Booking Module

Buid a custom Odoo module for managing hotel bookings. This module includes room management, booking management, and customer management. Additionally, implement a REST API for authentication and booking management using JWT.

The module is developed on Odoo version 14.

## Table of Contents

- [Prerequisites](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
  - [Register](#register)
  - [Login](#login)
  - [Booking](#booking)
- [Testing API](#testing-api)

## Prerequisites

This module require pyjwt and simplejson:

```bash
pip3 install pyjwt==2.8.0
pip3 install simplejson==3.19.2

```

Check full version libary in file:

```
requirements.txt
```

## Usage

1. **Module Interface:**

![Hotel Booking](static/img/hotel_booking.png)

![Hotel Customer](static/img/hotel_customer.png)

![Hotel Room](static/img/hotel_room.png)

2. **Manage Token User:**

The tokens, once generated, will be stored and managed here. Expired tokens will not be authenticated.

![Hotel Room](static/img/jwt_token_user.png)

3. **Define SECRET_KEY:**

SECRET_KEY is a secret string used for encoding and decoding tokens.

![Hotel Room](static/img/secret_key.png)

## API Endpoints

### Register

```
/api/auth/register
```

Based on the SECRET_KEY to encode data and generate tokens.

It will return the Token, user data, and status upon success.

If successful, it will create a **user portal** on the Odoo server.

### Login

```
/api/auth/login
```

Based on the SECRET_KEY to encode data and generate tokens.

Login authentication is based on the provided email and password. If authentication is successful, it will return the Token, user data, and status.

### Booking

```
/api/bookings
```

User authentication is based on the provided token. If the token is valid, it will proceed to create a hotel booking and return the hotel booking data and status

Only create a hotel booking if the room hotel status is 'available'.

## Testing API

Using Postman to testing the API.

### Test API register:

URL: yourlocalhost/api/auth/register

Method: POST

Headers: None

Body:

```bash
{
    "jsonrpc": "2.0",
    "params": {
        "name": "John Doe",
        "email": "john@inbox4us.xyz",
        "password": "password"
    }
}
```

**Return:**

```bash
{
    "jsonrpc": "2.0",
    "id": null,
    "result": {
        "success": true,
        "code": 200,
        "data": {
            "user": {
                "id": 62,
                "email": "john@inbox4us.xyz",
                "name": "John Doe"
            },
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjAwMjg0NzMsImlhdCI6MTcxNzQzNjQ3MywidXNlciI6NjIsImxvZ2luIjoiam9obkBpbmJveDR1cy54eXoifQ.5c_Y8j2LKK9RTmz73593RwuGVroQSDlBs9LtP_SPv1w"
        }
    }
}
```

### Test API login:

URL: yourlocalhost/api/auth/login

Method: POST

Headers: None

Body:

```bash
{
    "jsonrpc": "2.0",
    "params": {
        "email": "john@inbox4us.xyz",
        "password": "password"
    }
}
```

**Return:**

```bash
{
    "jsonrpc": "2.0",
    "id": null,
    "result": {
        "success": true,
        "code": 200,
        "data": {
            "user": {
                "id": 62,
                "email": "john@inbox4us.xyz",
                "name": "John Doe"
            },
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjAwMjg0OTcsImlhdCI6MTcxNzQzNjQ5NywidXNlciI6NjIsImxvZ2luIjoiam9obkBpbmJveDR1cy54eXoifQ.dER89lv_jPG9YyoTdfnkIpcEfjmN9vFxWHilKY9Cvug"
        }
    }
}
```

### Test API booking:

URL: yourlocalhost/api/bookings

Method: POST

Headers:

```
Authorization: Bearer <REPLACE_WITH_JWT_TOKEN>
```

Body:

```bash
{
    "jsonrpc": "2.0",
    "params": {
        "room_id": 2,
        "customer_id": 4,
        "checkin_date": "2022-01-01",
        "checkout_date": "2022-01-05"
    }
}
```

**Return:**

```bash
{
    "jsonrpc": "2.0",
    "id": null,
    "result": {
        "success": true,
        "code": 201,
        "data": {
            "booking": {
                "id": 16,
                "customer_id": [
                    4,
                    "Nguyễn Đức Thịnh"
                ],
                "room_id": [
                    2,
                    "2"
                ],
                "check_in_date": "2022-01-01",
                "check_out_date": "2022-01-05",
                "total_amount": 400.0,
                "display_name": "hotel.booking,16",
                "create_uid": [
                    62,
                    "John Doe"
                ],
                "create_date": "2024-06-03 17:44:31",
                "write_uid": [
                    62,
                    "John Doe"
                ],
                "write_date": "2024-06-03 17:44:31",
                "__last_update": "2024-06-03 17:44:31"
            }
        }
    }
}
```
