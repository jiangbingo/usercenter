from django.contrib import admin

# Register your models here.
from products.models import *

admin.site.register(ProductCategory)
admin.site.register(ProductBrand)
admin.site.register(ProductBrandSeries)
admin.site.register(Product)
admin.site.register(ProductCategoryAttribute)
admin.site.register(ProductCategoryAttributeValue)
admin.site.register(Manufactor)