from rest_framework import routers

from .attribute_views import AttributeViewSet
from .category_views import CategoryViewSet
from .checkupdate_views import CheckUpdateViewSet
from .distributor_views import DistributorViewSet
from .manufactory_views import ManufactoryViewSet
from .modelattr_views import ModelAttributeViewSet
from .product_views import ProductViewSet
from .series_views import SeriesViewSet

router = routers.SimpleRouter()
router.register(r'category', CategoryViewSet, 'cateogry')
router.register(r'attr', AttributeViewSet, 'attr')
router.register(r'products', ProductViewSet, 'product')
router.register(r'series', SeriesViewSet, 'series')
router.register(r'checkupdate', CheckUpdateViewSet, 'checkupdate')
router.register(r'manufactory', ManufactoryViewSet, 'manufactory')
router.register(r'distributor', DistributorViewSet, 'distributor')
router.register(r'modelattr', ModelAttributeViewSet, 'modelattr')
urlpatterns = router.urls
