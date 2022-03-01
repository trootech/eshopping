import pytest
from django.core.management import call_command
from django.urls import reverse
from oscar.core.compat import get_user_model
from oscar.core.loading import get_model
from pytest_django.asserts import assertTemplateUsed

WishList = get_model("wishlists", "Wishlist")
User = get_user_model()


# @pytest.fixture(scope='session')
# def django_db_setup(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         call_command('loaddata', 'oscar_data.json')


@pytest.fixture(scope="function")
def setup_admin_login(client, db):
    client.login(username='admin', password='admin')


@pytest.mark.django_db
def test_owner_has_access_for_wishlist_or_not(client, django_db_setup):
    """
    Tests that no user other than owner or user with whom wishlist has been shared
    has access to wishlist
    """
    wishlist = WishList.objects.get(name="Books")
    user_without_access = client.login(username='test1', password='test@1234')
    assert user_without_access, "Invalid credentials"
    resp = client.get(reverse('customer:wishlists-detail', kwargs={"key": wishlist.key}))
    assert resp.status_code == 404, "Do not have access, still able to access wishlist page"


def test_invite_user_url_exists(client, django_db_setup, setup_admin_login):
    """
    Tests whether invite user url from where owner can add users as shared users is working or not
    """
    wishlist = WishList.objects.get(name="Books")
    resp = client.get(reverse("customer:wishlist-shared-users", kwargs={"key": wishlist.key}))
    assert resp.status_code == 200, "Invite user page not accessible"
    assertTemplateUsed(resp, "oscar/customer/wishlists/wishlists_add_users.html")


def test_invite_users_page_accessible_for_shared_wishlist_only(client, django_db_setup, setup_admin_login):
    """
    Tests that invite users page accessible for shared wishlist only
    """
    catalogue_response = client.get("/catalogue/")
    assert catalogue_response.status_code == 200, "Catalogue page not accessible"
    dummy_wishlist = WishList.objects.create(name="dummy_wishlist", owner=catalogue_response.context["user"])
    assert dummy_wishlist.visibility == "Private", "Dummy Wishlist created is not private by default"
    resp = client.get(reverse("customer:wishlist-shared-users", kwargs={"key": dummy_wishlist.key}))
    assert resp.status_code == 404, "Invite user page should not be accessible for private wishlist"

    wishlist = WishList.objects.get(name="Books")
    resp = client.get(reverse("customer:wishlist-shared-users", kwargs={"key": wishlist.key}))
    assert resp.status_code == 200, "Invite user page should be accessible to shared wishlist"


def test_wishlist_list_page_has_shared_wishlists(client, django_db_setup, setup_admin_login):
    """
    Tests whether wishlists page has shared_with_users_list variable or not
    """
    wishlist = WishList.objects.get(name="Books")
    resp = client.get(reverse("customer:wishlist-shared-users", kwargs={"key": wishlist.key}))
    assert resp.context_data.get(
        "shared_with_users_list") is not None, "Response context should contain shared_with_users_list variable"


def test_invited_user_can_access_shared_wishlist_detail_page_or_not(client, django_db_setup, setup_admin_login):
    wishlist = WishList.objects.get(name="Books")

    user_to_invite = User.objects.get(username="test1")
    post_data = {
        "shared_with_users": [user_to_invite.id]
    }
    header = {'HTTP_ORIGIN': 'http://localhost:9000'}
    resp = client.post(reverse("customer:wishlist-shared-users", kwargs={"key": wishlist.key}), data=post_data,
                       **header)
    assert resp.status_code == 302, "Inviting users not working properly, as it should be redirected to wishlists list page"

    client.login(username='test1', password='test@1234')
    resp = client.get(reverse('customer:wishlists-detail', kwargs={"key": wishlist.key}))
    assert resp.status_code == 200, "Invited user cannot access shared wishlist detail page"

    client.login(username="admin", password="admin")
    resp = client.get(reverse('customer:wishlists-detail', kwargs={"key": wishlist.key}))
    assert resp.status_code != 404, "Already shared user earlier do not have access after new user was invited"


def test_removed_user_from_wishlist_has_no_longer_access_to_shared_wishlist(client, django_db_setup, setup_admin_login):
    """
    Tests whether user that have been removed from shared wishlist has access to shared wishlist detail
    page or not
    """
    wishlist = WishList.objects.get(name="Books")
    user_to_invite = User.objects.get(username="test1")
    post_data = {
        "shared_with_users": [user_to_invite.id]
    }
    header = {'HTTP_ORIGIN': 'http://localhost:9000'}
    resp = client.post(reverse("customer:wishlist-shared-users", kwargs={"key": wishlist.key}), post_data, **header)
    assert resp.status_code == 302, "Inviting users not working properly, as it should be redirected to wishlists list page"

    resp = client.post(
        reverse("customer:wishlist-shared-remove-user", kwargs={"key": wishlist.key, "user_pk": user_to_invite.pk}))
    assert resp.status_code == 302, "Removing user from wishlist not working properly, as it should be redirected to detail page"

    client.login(username='test1', password='test@1234')
    resp = client.get(reverse('customer:wishlists-detail', kwargs={"key": wishlist.key}))
    assert resp.status_code == 404, "Do not have access as removed from wishlist, still able to access wishlist page"
