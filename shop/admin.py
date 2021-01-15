from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review
from django.urls import reverse
from django.utils.safestring import mark_safe


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['content', 'id']


admin.site.register(Review, ReviewAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20


admin.site.register(Product, ProductAdmin)


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    fieldsets = [
        ('Product', {'fields': ['product'], }),
        ('Quantity', {'fields': ['quantity'], }),
        ('Price', {'fields': ['price'], }),
    ]
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False
    max_num = 0

def order_pdf(obj):
        url = reverse('admin_order_pdf', args=[obj.id])
        return mark_safe(f'<a href="{url}">PDF</a>') #mark_safe mean that it is saf 
order_pdf.short_description = 'Invoice'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'billingName', 'emailAddress', 'created',order_pdf]
    list_display_links = ('id', 'billingName')
    search_fields = ['id', 'billingName', 'emailAddress']
    readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created',
                       'billingName', 'billingAddress1', 'billingCity', 'billingPostcode',
                       'billingCountry', 'shippingName', 'shippingAddress1', 'shippingCity',
                       'shippingPostcode', 'shippingCountry']

    fieldsets = [
        ('ORDER INFORMATION', {'fields': ['id', 'token', 'total', 'created']}),
        ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1',
                                            'billingCity', 'billingPostcode', 'billingCountry', 'emailAddress']}),
        ('SHIPPING INFORMATION', {'fields': ['shippingName', 'shippingAddress1',
                                             'shippingCity', 'shippingPostcode', 'shippingCountry']}),
    ]

    inlines = [OrderItemAdmin,]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
    

#admin.site.register(Review)

# use memcache admin index site
admin.site.index_template = 'memcache_status/admin_index.html'

admin.site.site_header= 'T-Shopit Administration'
admin.site.site_title = 'T-Shopit'
admin.site.index_title = 'T-Shopit'