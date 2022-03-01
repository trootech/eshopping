from django import template
from oscar.core.loading import get_model

register = template.Library()

ProductAlert = get_model('customer', 'ProductAlert')


@register.simple_tag()
def check_if_product_has_alert(user, product):
    # Check if this user already have an alert for this product
    has_alert = False
    if user.is_authenticated:
        alerts = ProductAlert.objects.filter(
            product=product, user=user,
            status=ProductAlert.ACTIVE)
        has_alert = alerts.exists()
    return has_alert
