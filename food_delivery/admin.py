# admin.py (لإدارة Django Admin)
from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Driver)
admin.site.register(Delivery)
admin.site.register(Review)