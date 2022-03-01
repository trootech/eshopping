from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from oscar.core.compat import get_user_model
from oscar.core.loading import get_model

WishList = get_model("wishlists", "WishList")
User = get_user_model()


class WishListForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.owner = user

    class Meta:
        model = WishList
        fields = ('name', 'visibility')

    def clean_name(self):
        name = self.cleaned_data["name"]
        if WishList.objects.filter(name=self.cleaned_data["name"]).exists():
            raise ValidationError(_("Wishlist with name " + name + " already exists"))
        return name


class SharedWishlistAddUsersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["shared_with_users"].label = "Share your wishlist with other users"
        instance = kwargs.get("instance")

        # list of those users with whom wishlist has not been shared yet
        self.fields["shared_with_users"].queryset = User.objects.exclude(Q(id__in=instance.shared_with_users.all()) | Q(id=instance.owner.id))

    class Meta:
        model = WishList
        fields = ('shared_with_users',)

