from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from fastapi import FastAPI, APIRouter, HTTPException, Request
import os
import requests

from pydantic import BaseModel


from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from ..utils.rate_limit import limiter

# smtp_pass = os.environ["SIDSMTP"]
smtp_pass = os.environ["CONGSMTP"]
recaptcha_secret = os.environ["RECAPTCHA_SECRET_KEY"]


class EmailRequest(BaseModel):
    subject: str
    content: str
    response_token: str
class RecaptchaResponse(BaseModel):
    success: bool
    message: str


router = APIRouter()


@router.get("/check_email")
@limiter.limit("5/minute")
def email_check(request: Request):
    return {'ip':request.client.host}

@router.post("/email")
async def email(email_request: EmailRequest):
    try:
        if not email_request.response_token:
            return RecaptchaResponse(success=False, message='reCAPTCHA not completed.')

        verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': recaptcha_secret,
            'response': email_request.response_token,
        }
        response = requests.post(verification_url, data=payload)

        if response.json()['success']:
            # Create a message
            msg = MIMEMultipart()
            msg["From"] = "CMI Sales <sales@congruencemarketinsights.com>"
            msg["To"] = "sales@congruencemarketinsights.com"
            recipients = ["sales@congruencemarketinsights.com"]
            
            msg["Subject"] = email_request.subject

            # Add the HTML message body
            html_message = email_request.content
            msg.attach(MIMEText(html_message, "html"))

            # Create an SMTP server connection
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("sales@congruencemarketinsights.com", smtp_pass)
                server.sendmail(
                    "CMI Sales", recipients, msg.as_string()
                )

            return {"message": "Email sent successfully"}
        else:
            return RecaptchaResponse(success=False, message='reCAPTCHA verification failed.')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# @router.post("/email")
# async def email(email_request: EmailRequest):
#     try:
#         if not email_request.response_token:
#             return RecaptchaResponse(success=False, message='reCAPTCHA not completed.')

#         verification_url = 'https://www.google.com/recaptcha/api/siteverify'
#         payload = {
#             'secret': recaptcha_secret,
#             'response': email_request.response_token,
#         }
#         response = requests.post(verification_url, data=payload)

#         if response.json()['success']:
#             # Create a message
#             msg = MIMEMultipart()
#             msg["From"] = "Siddhant <siddhant.pandagle1998@gmail.com>"
#             msg["To"] = "siddhant.pandagle1998@gmail.com"
#             msg["Subject"] = email_request.subject

#             # Add the HTML message body
#             html_message = email_request.content
#             msg.attach(MIMEText(html_message, "html"))

#             # Create an SMTP server connection
#             with smtplib.SMTP("smtp.gmail.com", 587) as server:
#                 server.starttls()
#                 server.login("siddhant.pandagle1998", smtp_pass)
#                 server.sendmail(
#                     "Siddhant", "siddhant.pandagle1998@gmail.com", msg.as_string()
#                 )

#             return {"message": "Email sent successfully"}
#         else:
#             return RecaptchaResponse(success=False, message='reCAPTCHA verification failed.')

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
