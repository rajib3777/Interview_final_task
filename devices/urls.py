from django.urls import path
from .views import (
    DeviceCreateView,
    DeviceAutoDetectView,
    DeviceListView,
    DeviceDeleteView,
)

urlpatterns = [
    
    path('add/', DeviceCreateView.as_view(), name='device-add'),

    path('auto-add/', DeviceAutoDetectView.as_view(), name='device-auto-add'),

    path('list/', DeviceListView.as_view(), name='device-list'),

    path('delete/<int:pk>/', DeviceDeleteView.as_view(), name='device-delete'),
]
