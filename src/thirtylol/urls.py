"""
Definition of urls for thirtylol.
"""

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin

# from tastypie.api import Api
# from presenters.api.resources import PresenterResource,PlatformResource,TagResource,PresenterDetailResource
# v1_api = Api(api_name='v1')
# v1_api.register(PresenterResource())
# v1_api.register(PlatformResource())
# v1_api.register(TagResource())
# v1_api.register(PresenterDetailResource())

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'presenters.views.index', name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/', 'presenters.views.about', name='about'),
    url(r'^feedback/', 'presenters.views.feedback', name='feedback'),
    url(r'^presenters/', include('presenters.urls', namespace='presenters')),
    # url(r'api/', include(v1_api.urls)),
    url(r'^search/', include('haystack.urls')),
    url(r'^accounts/', include('accounts.urls')),

  ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)