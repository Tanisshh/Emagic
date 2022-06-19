from django.contrib import admin
from .models import Order, OrderProduct, Payment

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ['payment', 'user', 'orderd', 'product', 'product_price', 'quantity']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display=['full_name', 'order_number','email', 'address', 'status', 'is_orderd', 'created_at']
    list_filter= ['is_orderd', 'status']
    list_per_page= 20
    search_fields= ['first_name', 'last_name', 'phone', 'email']
    inlines = [OrderProductInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Payment)
