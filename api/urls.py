from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path('', views.ItemList.as_view(),name='item-list'),
    path('<int:pk>/', views.ItemDetail.as_view(),name='item-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
