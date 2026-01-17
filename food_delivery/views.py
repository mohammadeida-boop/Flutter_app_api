# views.py
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import *
from .serializers import *

# Authentication Views
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

# User Profile View
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Restaurant ViewSet
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def menus(self, request, pk=None):
        restaurant = self.get_object()
        menus = Menu.objects.filter(restaurant=restaurant, availability_status='available')
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data)

# Menu ViewSet
class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [AllowAny]

# Order ViewSet
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.order_status in ['pending', 'confirmed']:
            order.order_status = 'canceled'
            order.save()
            return Response({'message': 'تم إلغاء الطلب بنجاح'})
        return Response({'error': 'لا يمكن إلغاء الطلب حالياً'}, status=400)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

# Payment ViewSet
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # عرض المدفوعات الخاصة بطلبات المستخدم فقط
            user_orders = Order.objects.filter(user=self.request.user)
            return Payment.objects.filter(order__in=user_orders)
        return Payment.objects.none()
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        payment = self.get_object()
        # هنا يمكنك إضافة منطق معالجة الدفع
        payment.payment_status = 'completed'
        payment.save()
        return Response({'message': 'تمت معالجة الدفع بنجاح'})

# Driver ViewSet
class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        available_drivers = Driver.objects.filter(availability_status='available')
        serializer = self.get_serializer(available_drivers, many=True)
        return Response(serializer.data)

# Delivery ViewSet
class DeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # السائقين يرون التوصيلات الموكلة إليهم
            if hasattr(self.request.user, 'driver'):
                return Delivery.objects.filter(driver=self.request.user.driver)
            # المستخدمون يرون توصيلات طلباتهم
            user_orders = Order.objects.filter(user=self.request.user)
            return Delivery.objects.filter(order__in=user_orders)
        return Delivery.objects.none()
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        delivery = self.get_object()
        new_status = request.data.get('delivery_status')
        
        if new_status in dict(Delivery.DELIVERY_STATUS).keys():
            delivery.delivery_status = new_status
            if new_status == 'delivered':
                delivery.actual_time = timezone.now()
                # تحديث حالة الطلب أيضاً
                delivery.order.order_status = 'delivered'
                delivery.order.save()
            delivery.save()
            return Response({'message': 'تم تحديث حالة التوصيل'})
        
        return Response({'error': 'حالة غير صالحة'}, status=400)

# Review ViewSet
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)