from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import Coalesce
from .models import Customer, Product, Order, OrderItem
from .serializers import CustomerSerializer, ProductSerializer, OrderSerializer
from django.db import models


class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().select_related('customer').prefetch_related('items__product')
    serializer_class = OrderSerializer

@api_view(['GET'])
def sales_summary(request):
    # Apply date filters if provided
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    
    orders = Order.objects.all()
    
    if from_date:
        orders = orders.filter(order_date__gte=from_date)
    if to_date:
        orders = orders.filter(order_date__lte=to_date)
    
    total_sales = orders.aggregate(
        total_revenue=Coalesce(
            Sum(F('items__quantity') * F('items__product__price')),
            0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )['total_revenue']
    
    total_customers = Customer.objects.count()
    total_products_sold = OrderItem.objects.aggregate(
        total_quantity=Coalesce(Sum('quantity'), 0)
    )['total_quantity']
    
    total_orders = orders.count()
    
    return Response({
        'total_sales': total_sales,
        'total_customers': total_customers,
        'total_products_sold': total_products_sold,
        'total_orders': total_orders
    })

@api_view(['GET'])
def top_customers(request):
    # Apply date filters if provided
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    
    orders = Order.objects.all()
    
    if from_date:
        orders = orders.filter(order_date__gte=from_date)
    if to_date:
        orders = orders.filter(order_date__lte=to_date)
    
    top_customers = Customer.objects.annotate(
        total_spent=Coalesce(
            Sum(
                F('order__items__quantity') * F('order__items__product__price'),
                filter=models.Q(order__in=orders)
            ),
            0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        order_count=Count('order', filter=models.Q(order__in=orders))
    ).order_by('-total_spent')[:5]
    
    result = []
    for customer in top_customers:
        result.append({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'total_spent': customer.total_spent,
            'order_count': customer.order_count
        })
    
    return Response(result)

@api_view(['GET'])
def top_products(request):
    # Apply date filters if provided
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    
    order_items = OrderItem.objects.all()
    
    if from_date:
        order_items = order_items.filter(order__order_date__gte=from_date)
    if to_date:
        order_items = order_items.filter(order__order_date__lte=to_date)
    
    top_products = Product.objects.annotate(
        total_sold=Coalesce(
            Sum('orderitem__quantity', filter=models.Q(orderitem__in=order_items)),
            0
        ),
        total_revenue=Coalesce(
            Sum(F('orderitem__quantity') * F('price'), filter=models.Q(orderitem__in=order_items)),
            0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by('-total_sold')[:5]
    
    result = []
    for product in top_products:
        result.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'total_sold': product.total_sold,
            'total_revenue': product.total_revenue
        })
    
    return Response(result)