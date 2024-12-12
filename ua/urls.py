from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from myapp.views import AddToCartView, AdminOrderView, CustomerOrderView, DashboardView, ProductDeleteView, ProductUpdateView, RegisterView, LoginView, RemoveFromCartView, UpdateCartQuantityView
from myapp.views import ProductListView, ProductCreateView, CartView, OrderView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/products/', ProductListView.as_view(), name='product_list'),  # For all users to view products
    path('api/products/create/', ProductCreateView.as_view(), name='product_create'),  # Only for authenticated users
    path('api/order/', OrderView.as_view(), name='order'),
    path('api/products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),  # Admin only access
    path('api/products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),  # Admin only access
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='view_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update/', UpdateCartQuantityView.as_view(), name='update_cart'),
    path('admin/orders/<int:pk>/', AdminOrderView.as_view(), name='admin_order_update'),
    path('customer/orders/', CustomerOrderView.as_view(), name='customer_orders'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

