from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import HasResourcePermission, IsAuthenticated

MOCK_ORDERS = [
    {'id': 1, 'title': 'Заказ #1001', 'amount': 15000, 'status': 'new'},
    {'id': 2, 'title': 'Заказ #1002', 'amount': 3200, 'status': 'done'},
    {'id': 3, 'title': 'Заказ #1003', 'amount': 8700, 'status': 'processing'},
]

MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Ноутбук', 'price': 75000, 'category': 'electronics'},
    {'id': 2, 'name': 'Клавиатура', 'price': 3500, 'category': 'electronics'},
    {'id': 3, 'name': 'Стул офисный', 'price': 12000, 'category': 'furniture'},
]

MOCK_REPORTS = [
    {'id': 1, 'title': 'Отчёт по продажам Q1', 'type': 'sales'},
    {'id': 2, 'title': 'Отчёт по складу', 'type': 'inventory'},
]


class OrderListView(APIView):
    permission_classes = [IsAuthenticated, HasResourcePermission]
    resource = 'orders'

    def get(self, request):
        return Response({'count': len(MOCK_ORDERS), 'results': MOCK_ORDERS})

    def post(self, request):
        new_order = {
            'id': len(MOCK_ORDERS) + 1,
            'title': request.data.get('title', 'Новый заказ'),
            'amount': request.data.get('amount', 0),
            'status': 'new',
        }
        return Response(new_order, status=201)


class ProductListView(APIView):
    permission_classes = [IsAuthenticated, HasResourcePermission]
    resource = 'products'
    action_permission = 'read'

    def get(self, request):
        return Response({'count': len(MOCK_PRODUCTS), 'results': MOCK_PRODUCTS})


class ReportListView(APIView):
    permission_classes = [IsAuthenticated, HasResourcePermission]
    resource = 'reports'
    action_permission = 'read'

    def get(self, request):
        return Response({'count': len(MOCK_REPORTS), 'results': MOCK_REPORTS})
