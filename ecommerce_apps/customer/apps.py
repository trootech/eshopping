import oscar.apps.customer.apps as apps
from django.urls import path
from oscar.core.loading import get_class


class CustomerConfig(apps.CustomerConfig):
    name = 'ecommerce_apps.customer'
    namespace = 'customer'
    label = 'customer'

    def __init__(self, app_name, app_module, namespace=None, **kwargs):
        super(CustomerConfig, self).__init__(app_name, app_module, namespace, **kwargs)
        self.wishlist_shared_remove_user = None
        self.wishlists_add_users_to_shared_wishlist = None

    def ready(self):
        super(CustomerConfig, self).ready()
        from . import signals
        self.wishlists_add_users_to_shared_wishlist = get_class(
            'customer.wishlists.views', 'SharedWishListAddUsersView')
        self.wishlist_shared_remove_user = get_class(
            'customer.wishlists.views', 'SharedWishlistRemoveUser')

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path('wishlists/shared/<str:key>/users/', self.wishlists_add_users_to_shared_wishlist.as_view(), name='wishlist-shared-users'),
            path('wishlists/shared/<str:key>/users/<int:user_pk>/remove/', self.wishlist_shared_remove_user.as_view(), name='wishlist-shared-remove-user'),
        ]
        return self.post_process_urls(urls)
