from django.urls import path

from business.views import OrderListView, ProductListView, ReportListView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('reports/', ReportListView.as_view(), name='report-list'),
]
