from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Basic CRUD endpoints
    path('api/customers/', views.CustomerListCreateView.as_view(), name='customer-list'),
    path('api/products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('api/orders/', views.OrderListCreateView.as_view(), name='order-list'),
    
    # Analytics endpoints
    path('api/analytics/sales-summary/', views.sales_summary, name='sales-summary'),
    path('api/analytics/top-customers/', views.top_customers, name='top-customers'),
    path('api/analytics/top-products/', views.top_products, name='top-products'),
]