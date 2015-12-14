from tastypie import fields
from tastypie.resources import ModelResource
from presenters.models import Presenter, Platform, Tag, PresenterDetail
from tastypie.constants import ALL


class PlatformResource(ModelResource):
    class Meta:
        queryset = Platform.objects.all()
        allowed_methods = ['get']


class TagResource(ModelResource):
    class Meta:
        queryset = Tag.objects.all()
        allowed_methods = ['get']


class PresenterDetailResource(ModelResource):
    class Meta:
        queryset = PresenterDetail.objects.all()
        allowed_methods = ['get']
        # resource_name = 'presenter_detail'


class PresenterResource(ModelResource):
    platform = fields.ForeignKey(PlatformResource, 'platform', full=True)
    tags = fields.ToManyField(TagResource, 'tag', full=True)
    detail = fields.OneToOneField(
        PresenterDetailResource,
        'presenterdetail',
        full=True)

    def apply_sorting(self, obj_list, options=None):
        if options and "sort" in options:
            if options['sort'] == 'showing':
                return obj_list.order_by('-presenterdetail__showing')
            else:
                return obj_list.order_by(options['sort'])
        return super(PresenterResource, self).apply_sorting(obj_list, options)

    # showing = fields.BooleanField(readonly=True)
    # def dehydrate_showing(self, bundle):
    #     print type(bundle.obj), type(bundle.data)
    #     print dir(type(bundle.obj))
    #     return bundle.obj.presenterdetail.showing

    # def build_filters(self, filters=None):
    #     print filters
    #     if filters is None:
    #         filters = {}

    #     orm_filters = super(PresenterResource, self).build_filters(filters)
    #     print type(orm_filters), orm_filters
    #     if 'q' in filters:
    #         pass
    #     return orm_filters
    class Meta:
        queryset = Presenter.objects.all()
        allowed_methods = ['get']

        filtering = {
            "nickname": ALL,
        }
