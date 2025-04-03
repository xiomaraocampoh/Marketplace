from django.contrib import admin
from .models import Product, Category, Order, OrderItem, Cart

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'created_at')
    ordering = ('-created_at',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'order_date')

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__user__username', 'product__name')
    list_filter = ('order',)
    ordering = ('-order',)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__username', 'product__name')
    list_filter = ('user',)
    ordering = ('-user',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, CartAdmin)

