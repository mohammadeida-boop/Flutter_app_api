# models.py
# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('يجب إدخال البريد الإلكتروني')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Add this
        return self.create_user(email, password, **extra_fields)

# User Model
class User(AbstractBaseUser, PermissionsMixin):  # Add PermissionsMixin
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='الاسم')
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    phone = models.CharField(max_length=15, verbose_name='رقم الهاتف')
    address = models.TextField(verbose_name='العنوان', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Required fields for Django admin
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    is_staff = models.BooleanField(default=False, verbose_name='موظف')
    is_superuser = models.BooleanField(default=False, verbose_name='مدير')
    
    @property
    def is_driver(self):
        try:
            return hasattr(self, 'driver')
        except:
            return False
    @property
    def id(self):
        return self.user_id
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'

# Restaurant Model
class Restaurant(models.Model):
    restaurant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='اسم المطعم')
    address = models.TextField(verbose_name='عنوان المطعم')
    phone = models.CharField(max_length=15, verbose_name='هاتف المطعم')
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0,
        verbose_name='التقييم'
    )
    cuisine_type = models.CharField(max_length=100, verbose_name='نوع المطبخ')
    
    def __str__(self):
        return self.name

# Menu Model
class Menu(models.Model):
    AVAILABILITY_STATUS = [
        ('available', 'متاح'),
        ('unavailable', 'غير متاح'),
        ('out_of_stock', 'نفذت الكمية'),
    ]
    
    menu_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(
        Restaurant, 
        on_delete=models.CASCADE,
        related_name='menus',
        verbose_name='المطعم'
    )
    item_name = models.CharField(max_length=200, verbose_name='اسم العنصر')
    description = models.TextField(blank=True, verbose_name='الوصف')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='السعر'
    )
    image_url = models.URLField(max_length=500, blank=True, verbose_name='رابط الصورة')
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default='available',
        verbose_name='حالة التوفر'
    )
    
    def __str__(self):
        return f"{self.item_name} - {self.restaurant.name}"

# Order Model
class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'تم التأكيد'),
        ('preparing', 'قيد التحضير'),
        ('on_the_way', 'في الطريق'),
        ('delivered', 'تم التسليم'),
        ('canceled', 'ملغي'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='المستخدم'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='المطعم'
    )
    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='pending',
        verbose_name='حالة الطلب'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='المبلغ الإجمالي'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    def __str__(self):
        return f"Order #{self.order_id} - {self.user.email}"

# OrderItem Model
class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='الطلب'
    )
    menu_item = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='عنصر القائمة'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='الكمية')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='السعر'
    )
    
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.item_name}"

# Payment Model
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('card', 'بطاقة ائتمانية'),
        ('paypal', 'PayPal'),
        ('cash', 'نقدي عند الاستلام'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'قيد الانتظار'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('refunded', 'تم الاسترداد'),
    ]
    
    payment_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name='الطلب'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name='طريقة الدفع'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name='حالة الدفع'
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='رقم المعاملة'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='المبلغ'
    )
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الدفع')
    
    def __str__(self):
        return f"Payment #{self.payment_id} - {self.order.order_id}"

# Driver Model
class Driver(models.Model):
    AVAILABILITY_STATUS = [
        ('available', 'متاح'),
        ('busy', 'مشغول'),
        ('offline', 'غير متصل'),
    ]
    
    driver_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='الاسم')
    phone = models.CharField(max_length=15, verbose_name='رقم الهاتف')
    vehicle_type = models.CharField(max_length=50, verbose_name='نوع المركبة')
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default='available',
        verbose_name='حالة التوفر'
    )
    
    def __str__(self):
        return self.name

# Delivery Model
class Delivery(models.Model):
    DELIVERY_STATUS = [
        ('assigned', 'تم التعيين'),
        ('on_the_way', 'في الطريق'),
        ('delivered', 'تم التسليم'),
        ('canceled', 'ملغي'),
    ]
    
    delivery_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery',
        verbose_name='الطلب'
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deliveries',
        verbose_name='السائق'
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS,
        default='assigned',
        verbose_name='حالة التوصيل'
    )
    estimated_time = models.DateTimeField(verbose_name='الوقت المقدر للتوصيل')
    actual_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='الوقت الفعلي للتوصيل'
    )
    
    def __str__(self):
        return f"Delivery #{self.delivery_id} - Order #{self.order.order_id}"

# Review Model
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='المستخدم'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='المطعم'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='الطلب'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='التقييم'
    )
    comment = models.TextField(blank=True, verbose_name='تعليق')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.restaurant.name}"