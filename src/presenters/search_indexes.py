# -*- coding: utf-8 -*-
from .models import Presenter
from haystack import indexes

class PresenterIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    nickname = indexes.CharField(model_attr='nickname')
    introduce = indexes.CharField(model_attr='introduce')

    def get_model(self):
        return Presenter

    def index_queryset(self, using=None):
        return self.get_model().objects.all()