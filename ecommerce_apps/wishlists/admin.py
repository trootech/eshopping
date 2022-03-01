from django.contrib import admin
from oscar.core.loading import get_model


class WishListAdmin(admin.ModelAdmin):
    list_display = ("name", "visibility")


admin.site.register(get_model("wishlists", "Wishlist"), WishListAdmin)
