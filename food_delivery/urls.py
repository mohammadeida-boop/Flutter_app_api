# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    LoginView,
    UserProfileView,
    RestaurantViewSet,
    MenuViewSet,
    OrderViewSet,
    PaymentViewSet,
    DriverViewSet,
    DeliveryViewSet,
    ReviewViewSet,
)

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'drivers', DriverViewSet)
router.register(r'deliveries', DeliveryViewSet, basename='delivery')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # API
    path('', include(router.urls)),
]