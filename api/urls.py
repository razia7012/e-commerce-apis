from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    ProductViewSet,
    CategoryViewSet,
    CartView,
    CartItemView,
    OrderView,
    OrderStatusView,
    ApplyCouponView,
    CouponCreateView,
    LogoutView,
)


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/item/", CartItemView.as_view(), name="cart-item-delete"),
    path("order/", OrderView.as_view(), name="order-create"),
    path("order/status/", OrderStatusView.as_view(), name="order-status"),
    path("order/apply-coupon/", ApplyCouponView.as_view(), name="apply-coupon"),
    path("coupon/create/", CouponCreateView.as_view(), name="coupon-create"),
    path("", include(router.urls)),
]
