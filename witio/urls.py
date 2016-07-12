from django.conf.urls import url

from .views import WitioView

urlpatterns = [
    url(r'^$', WitioView.as_view())
]
