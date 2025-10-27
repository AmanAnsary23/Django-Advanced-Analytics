from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Customer, Product, Order, OrderItem
from django.utils import timezone

class AnalyticsAPITestCase(APITestCase):
    def setUp(self):
        # Create test data
        self.customer1 = Customer.objects.create(name="John Doe", email="john@example.com")
        self.customer2 = Customer.objects.create(name="Jane Smith", email="jane@example.com")
        
        self.product1 = Product.objects.create(name="Laptop", price=1000.00)
        self.product2 = Product.objects.create(name="Mouse", price=25.50)
        self.product3 = Product.objects.create(name="Keyboard", price=75.00)
        
        # Create orders
        order1 = Order.objects.create(customer=self.customer1)
        OrderItem.objects.create(order=order1, product=self.product1, quantity=1)
        OrderItem.objects.create(order=order1, product=self.product2, quantity=2)
        
        order2 = Order.objects.create(customer=self.customer2)
        OrderItem.objects.create(order=order2, product=self.product1, quantity=1)
        OrderItem.objects.create(order=order2, product=self.product3, quantity=3)
        
        # Get JWT token
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='testuser', password='testpass')
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_sales_summary(self):
        url = reverse('sales-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertIn('total_sales', data)
        self.assertIn('total_customers', data)
        self.assertIn('total_products_sold', data)
        self.assertIn('total_orders', data)
        
        # Calculate expected values
        expected_sales = (1000 + (25.50 * 2)) + (1000 + (75 * 3))
        self.assertEqual(float(data['total_sales']), expected_sales)
        self.assertEqual(data['total_customers'], 2)
        self.assertEqual(data['total_products_sold'], 7)  # 1+2+1+3
        self.assertEqual(data['total_orders'], 2)

class CustomerAPITestCase(APITestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='testuser', password='testpass')
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_customer(self):
        url = reverse('customer-list')
        data = {
            'name': 'Test Customer',
            'email': 'test@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().name, 'Test Customer')