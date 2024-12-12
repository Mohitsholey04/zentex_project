from django.contrib import admin
from .models import Product, Cart, Order
from django.utils.html import format_html

# Register Cart model
admin.site.register(Cart)

# Register Product model with a custom admin class
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />'.format(obj.image.url))
        return "No Image"

# Register Order model with a custom admin class
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'ordered_at')
    list_filter = ('status', 'ordered_at')
    search_fields = ('user__username', 'product__name')
