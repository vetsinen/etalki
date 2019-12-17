from django.urls import path
from . import views

urlpatterns = [
    path('slotmaker/', views.slotmaker),
    path('slots/', views.slots),
    path('timeoffset/', views.timeoffset),
    path('callback/', views.callback),
    path('unbook/', views.unbook),
    path('alllessons/', views.alllessons, name='alllessons'),
    path('', views.booked, name='home'),
]