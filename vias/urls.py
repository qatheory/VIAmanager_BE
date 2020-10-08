from django.urls import path
from vias import views

urlpatterns = [
    path('vias/', views.ViaList.as_view()),
    path('via/<int:pk>/', views.ViaDetail.as_view()),
]
