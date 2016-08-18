from django.conf.urls import include, url, patterns
from products.views import *

urlpatterns = [
    #products manage
    url(r'pdt/$', ProductView.as_view(), name='product'),

    #category manage
    url(r'category/$', CategoryView.as_view(), name='category'),

    # import
    url(r'import/$', import_xls, name='import'),

    url(r'export/$', export_xls, name='export'),

    url(r'product/file/upload/$', upload_product_file, name='product-file-upload'),
    url(r'product/preview/upload/$', upload_product_preview,
        name='product-preview-upload'),
]