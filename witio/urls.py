from django.conf.urls import url

from .views import WitioView

urlpatterns = [
    url(r'^9e2cdb27a565ff4cdd86e6f3eb4228033ac8c924e4167ea430/$', WitioView.as_view())
]
