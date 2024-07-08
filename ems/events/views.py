from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import Event, CustomUser, Ticket, Notification
from .serializers import CustomUserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from .serializers import EventSerializer, TicketSerializer, NotificationSerializer


from .forms import CustomUserCreationForm

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'register.html', {'form': form})


# User login view
class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect(reverse('event-list-create'))
        return render(request, 'login.html', {'form': form})

# User logout view
def logout_view(request):
    auth_logout(request)
    return redirect('login')


class CanViewOrCreateEvents(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # Allow participants to view events but not create them
            if request.user.role == 'participant' and request.method in permissions.SAFE_METHODS:
                return True
            # Allow organizers to view and create events
            if request.user.role == 'organizer':
                return True
        return False

class IsOrganizer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == CustomUser.ORGANIZER



class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewOrCreateEvents]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class EventRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

class IsParticipant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == CustomUser.PARTICIPANT

class TicketBookingView(generics.CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def create(self, request, *args, **kwargs):
        event_pk = kwargs.get('event_pk')
        event = get_object_or_404(Event, pk=event_pk)

        # Check if the participant is the current logged-in user
        if request.user != event.organizer:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(participant=request.user, event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "You cannot book tickets for your own event."}, status=status.HTTP_400_BAD_REQUEST)

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]  # Only admin can create notifications

    def perform_create(self, serializer):
        serializer.save()
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

# View for updating the read status of notifications
class NotificationUpdateView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def put(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.read = not notification.read
        notification.save()
        return Response(self.get_serializer(notification).data)