from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('detail/<uuid:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('edit/<uuid:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('cancel/<uuid:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('doctor-update/<uuid:appointment_id>/', views.doctor_update_appointment, name='doctor_update_appointment'),
    path('available-slots/', views.get_available_slots, name='get_available_slots'),
    path('doctors/', views.doctor_list, name='doctor_list'),
]
