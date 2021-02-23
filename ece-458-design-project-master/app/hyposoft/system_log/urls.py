from django.urls import path
from .views import LogView

urlpatterns = [
    path('EntryList', LogView.as_view())
]
