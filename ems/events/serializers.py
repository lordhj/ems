from rest_framework import serializers
from .models import CustomUser, Event, Ticket, Notification

# CustomUser Serializer
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            role=validated_data['role'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance

# Event Serializer
class EventSerializer(serializers.ModelSerializer):
    organizer = CustomUserSerializer(read_only=True)
    organizer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.ORGANIZER), write_only=True, source='organizer'
    )

    class Meta:
        model = Event
        fields = '__all__'

# Ticket Serializer
class TicketSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), write_only=True, source='event'
    )
    participant = CustomUserSerializer(read_only=True)
    participant_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role=CustomUser.PARTICIPANT), write_only=True, source='participant'
    )

    class Meta:
        model = Ticket
        fields = ['id', 'event', 'event_id', 'participant', 'participant_id', 'purchase_time']

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), write_only=True, source='user'
    )

    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_id', 'message', 'read', 'created_at']

    @classmethod
    def create_ticket_notification(cls, participant, event):
        message = f"Ticket booked for event '{event.title}'"
        cls.objects.create(user=participant, message=message)

    @classmethod
    def create_event_notification(cls, organizer, event):
        message = f"Ticket booked for your event '{event.title}'"
        cls.objects.create(user=organizer, message=message)
