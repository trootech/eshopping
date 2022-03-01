from django.db.models.signals import m2m_changed
from oscar.core.loading import get_model

WishList = get_model("wishlists", "Wishlist")


def shared_users_changed(sender, **kwargs):
    """
    This signal is written to not clear earlier shared users when new shared users are added

    By default, in save_m2m method, first whole list is cleared and then new records are added i.e. clear()
    method is called, then add() method is called due to which previous records are deleted and list has new records only
    For example : Wishlist was shared with two users : user A and user B
    Now, if owner has to select another user, the dropdown will have list of users except users already
    added (i.e. user A and user B). Suppose, owner selects user C, then previous users, user A and user B
    will be removed due to clear method being called.

    Whenever post_remove method is called, we store set having ids which have to added in m2m
    field with earlier records(user A and user B as per example) in extra attr(_shared_ids) and then
    update pk_set on pre_add method call with ids in extra attribute _shared_ids
    So, even though clear method is called, new list will have new records as well as
    previous records (user A, user B, user C)
    """
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    action = kwargs.pop('action', None)
    if action == "post_remove":
        instance._shared_ids = pk_set
    if action == "pre_add":
        if getattr(instance, '_shared_ids', None):
            pk_set.update(set(instance._shared_ids))


m2m_changed.connect(shared_users_changed, sender=WishList.shared_with_users.through)
