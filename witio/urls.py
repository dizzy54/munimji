from django.conf.urls import url

from .views import WitioView

urlpatterns = [
    url(r'^witio/$', WitioView.as_view())
]
