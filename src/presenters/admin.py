from django.contrib import admin
from .models import Presenter, PresenterDetail, Platform, Tag

admin.site.register(Presenter)
admin.site.register(PresenterDetail)
admin.site.register(Platform)
admin.site.register(Tag)
