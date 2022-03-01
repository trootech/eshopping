import pytest
from django.urls import reverse
from oscar.core.loading import get_model

WishList = get_model("wishlists", "Wishlist")


@pytest.mark.django_db
def test_for_duplicate_name_of_wishlists(client, django_db_setup):
    """Tests that same name for two wishlists are not saved"""
    client.login(username="admin", password="admin")
    post_data = {
        "name": "Books",
        "visibility": "Shared"
    }
    resp = client.post(reverse("customer:wishlists-create"), post_data)
    assert resp.context and resp.context.get("form") and resp.context.get("form").errors and resp.context.get(
        'form').errors.get("name") is not None, "Wishlists with duplicate name cannot be created"


@pytest.mark.django_db
def test_users_list_should_not_contain_already_invited_users(client, django_db_setup):
    """
    Tests if already invited users are excluded from the list having list of users
    from which owner will select users to be invited
    """
    client.login(username="admin", password="admin")
    wishlist = WishList.objects.get(name="Books")
    already_in_shared_users = wishlist.shared_with_users.all()
    resp = client.get(reverse("customer:wishlist-shared-users", kwargs={"key": wishlist.key}))
    form_users = resp.context_data["form"].fields["shared_with_users"].queryset
    assert not form_users.intersection(
        already_in_shared_users).exists(), "Already shared users should not be in form list containing list of users to be invited"
