from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^(?P<presenter_id>\d+)$', views.detail, name='detail'),
    url('^feedback$', views.feedback, name='feedback'),
    url('^about$', views.about, name='about'),
    url('^fetch$', views.fetch, name='fetch'),
]
