from django.urls import path
from .views import RegisterView, LoginView, logout_view
from .views import EventListCreateView, EventRetrieveUpdateDestroyView, TicketBookingView, NotificationListView, NotificationUpdateView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/events/', EventListCreateView.as_view(), name='event-list-create'),
    path('api/events/<int:pk>/', EventRetrieveUpdateDestroyView.as_view(), name='event-detail'),
    path('api/events/<int:event_pk>/book/', TicketBookingView.as_view(), name='book-ticket'),
    path('api/notifications/', NotificationListView.as_view(), name='notification-list'),
    path('api/notifications/<int:pk>/', NotificationUpdateView.as_view(), name='notification-detail'),
]