# myapp/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta

@shared_task
def send_ticket_email(participant_email, event_title):
    subject = f"Ticket booked for {event_title}"
    message = f"Dear Participant, you have successfully booked a ticket for the event: {event_title}."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [participant_email]
    send_mail(subject, message, email_from, recipient_list)

@shared_task
def send_event_reminder(event_id):
    from .models import Event, Ticket
    event = Event.objects.get(id=event_id)
    participants = Ticket.objects.filter(event=event).values_list('participant__email', flat=True)
    subject = f"Reminder for upcoming event: {event.title}"
    message = f"Dear Participant, this is a reminder for the upcoming event: {event.title} scheduled at {event.start_time}."
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, list(participants))
