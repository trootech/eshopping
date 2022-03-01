from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import UpdateView, ListView
from oscar.apps.customer.mixins import PageTitleMixin
from oscar.core.loading import get_model, get_class

from ..tasks import send_shared_wishlist_invite_mail

User = get_user_model()
Product = get_model("catalogue", "Product")
WishList = get_model("wishlists", "Wishlist")
SharedWishlistAddUsersForm = get_class("wishlists.forms", "SharedWishlistAddUsersForm")


class WishListListView(PageTitleMixin, ListView):
    context_object_name = active_tab = "wishlists"
    template_name = 'oscar/customer/wishlists/wishlists_list.html'
    page_title = _('Wish Lists')

    def get_queryset(self):
        """
        Return a list of all the wishlists created by or shared with the authenticated user.
        """
        wishlists = WishList.objects.filter(Q(owner=self.request.user) | Q(shared_with_users__in=[self.request.user])).distinct()
        return wishlists


class SharedWishListAddUsersView(PageTitleMixin, UpdateView):
    """
    Adds a user to shared wishlist

    - If the wishlist is not shared, raise error
    - Email will be sent to shared user, on clicking of the link, he can see shared wishlist from his dashboard
    - By default, another user can edit the wishlist
    """
    template_name = 'oscar/customer/wishlists/wishlists_add_users.html'
    active_tab = "wishlists"
    model = WishList
    form_class = SharedWishlistAddUsersForm

    def get_object(self, queryset=None):
        wishlist = get_object_or_404(WishList, key=self.kwargs["key"])
        if wishlist.visibility == "Shared" and wishlist.is_allowed_to_see(self.request.user):
            return wishlist
        else:
            raise Http404

    def get_page_title(self):
        return self.object.name

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["shared_with_users_list"] = self.object.shared_with_users
        return ctx

    def form_valid(self, form):
        super().form_valid(form)
        # sending mail to user with whom wishlists has been shared with link
        shared_user_ids = form.data.getlist("shared_with_users")
        recipient_email = User.objects.filter(id__in=shared_user_ids).values_list("email", flat=True)
        username = self.request.user.username
        site_url = self.request.META["HTTP_ORIGIN"]
        redirect_link = site_url + reverse('customer:wishlists-detail', kwargs={"key": self.object.key})
        subject = "Invitation for viewing wishlist shared with you"
        message = "{} has shared his wishlist with you. Please click on link below to view the wishlist {}".format(
            username, redirect_link)
        from_email = settings.EMAIL_HOST_USER
        send_shared_wishlist_invite_mail.delay(subject, message, from_email, list(recipient_email))

        messages.success(self.request, _('Wishlist shared with users ' + ','.join(list(recipient_email))))
        return redirect('customer:wishlists-list')


class SharedWishlistRemoveUser(PageTitleMixin, View):
    active_tab = "wishlists"

    def dispatch(self, request, *args, **kwargs):
        if "remove" in request.path and self.kwargs.get("key") and self.kwargs.get("user_pk"):
            return self.delete(self, request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(WishList, key=self.kwargs["key"])

    def delete(self, request, *args, **kwargs):
        """
        Removes user from list of users to whom wishlist has been shared
        Sends mail to user who has been removed
        """
        wishlist = self.get_object()
        user = User.objects.get(id=kwargs.get("user_pk"))
        wishlist.shared_with_users.remove(user)

        # sending mail to user for his removal from the shared wishlist
        subject = "Removed from wishlist shared with you earlier"
        message = "You wont be able to view {} wishlist shared by you earlier as you have been removed from the list".format(
            wishlist.name)
        from_email = settings.EMAIL_HOST_USER
        recipient_email = user.email
        send_shared_wishlist_invite_mail.delay(subject, message, from_email, [recipient_email])

        messages.success(self.request, "User removed from the wishlist")
        return redirect(reverse('customer:wishlist-shared-users', kwargs={"key": kwargs["key"]}))
