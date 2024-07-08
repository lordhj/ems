from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from .tasks import send_ticket_email, send_event_reminder
from datetime import timedelta

# Custom User model extending Django's built-in User model
class CustomUser(AbstractUser):
    # Define roles as choices
    ORGANIZER = 'organizer'
    PARTICIPANT = 'participant'
    ROLE_CHOICES = [
        (ORGANIZER, 'Organizer'),
        (PARTICIPANT, 'Participant'),
    ]

    # Additional fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PARTICIPANT)

    def __str__(self):
        return self.username

# Notification model
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} created at {self.created_at}"

    @classmethod
    def create_ticket_notification(cls, participant, event):
        message = f"Ticket booked for event '{event.title}'"
        cls.objects.create(user=participant, message=message)

    @classmethod
    def create_event_notification(cls, organizer, event):
        message = f"Ticket booked for your event '{event.title}'"
        cls.objects.create(user=organizer, message=message)


# Event model
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


# Ticket model
class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    purchase_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket for {self.event.title} purchased by {self.participant.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Notification.create_ticket_notification(self.participant, self.event)
        Notification.create_event_notification(self.event.organizer, self.event)
        send_ticket_email.delay(self.participant.email, self.event.title)
        send_event_reminder.apply_async((self.event.id,), eta=self.event.start_time - timedelta(hours=1))

