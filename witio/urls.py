from django.conf.urls import url

from .views import WitioView, SplitwiseOauthRedirect

urlpatterns = [
    url(r'^$', WitioView.as_view()),
    url(r'^splitwise-redirect/$', SplitwiseOauthRedirect.as_view()),
]
