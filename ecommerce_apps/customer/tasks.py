import logging
from smtplib import SMTPException

from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_shared_wishlist_invite_mail(subject, message, from_email, recipient_email):
    """Sends mail to user with whom owner has shared the wishlist"""
    try:
        send_mail(subject, message, from_email, recipient_email, fail_silently=False)
    except SMTPException as error:
        logging.error("Error occurred while sending email : {}".format(error))
