from django.db import models
from oscar.apps.wishlists.abstract_models import AbstractWishList
from oscar.core.compat import AUTH_USER_MODEL


class Wishlist(AbstractWishList):
    """Model overridden to add functionality of sharing wishlist to users"""
    shared_with_users = models.ManyToManyField(AUTH_USER_MODEL, related_name="shared_wishlists")

    def is_allowed_to_see(self, user):
        """
        Return if user has permission to view wishlist

        User can view wishlist in one of the cases : wishlist is public or wishlist has been shared with user or user has created the wishlist
        """
        if self.visibility == self.PUBLIC:
            return True
        elif self.visibility == self.SHARED and user in self.shared_with_users.all():
            return True
        else:
            return user == self.owner


from oscar.apps.wishlists.models import *  # noqa isort:skip
