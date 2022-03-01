from collections import OrderedDict

from django.conf import settings
from haystack.query import SearchQuerySet


def base_sqs(categories=None):
    """
    Return the base SearchQuerySet for Haystack searches.

    This method is overridden so that dynamic facets can be added when categories are selected
    As we cannot add dynamic facets i.e. attributes of products directly in OSCAR_SEARCH_FACETS setting,
    we update OSCAR_SEARCH_FACETS with dynamic attributes of products of categories selected
    """
    sqs = SearchQuerySet()

    # adding dynamic facet field values for attribute
    from oscar.core.loading import get_model
    Product = get_model("catalogue", "Product")

    # remove all dynamic attributes as new dynamic attributes according to category selected will be
    # appended to the list and earlier attributes will remain as it is in facets list
    settings.OSCAR_SEARCH_FACETS["fields"] = OrderedDict(
        {key: value for key, value in settings.OSCAR_SEARCH_FACETS["fields"].items() if "_s" not in key})

    # show facets of attributes only when any category is selected
    if categories:
        products = Product.objects.filter(categories__slug__in=categories.values_list('slug', flat=True))
        if products:
            dynamic_attr_values = set(products.values_list('attribute_values__attribute__name', flat=True))
            for each_dynamic_attr in dynamic_attr_values:
                updated_attr = each_dynamic_attr.lower() + "_s"
                settings.OSCAR_SEARCH_FACETS["fields"].update(
                    {updated_attr: {"name": each_dynamic_attr, "field": updated_attr}})

    for facet in settings.OSCAR_SEARCH_FACETS['fields'].values():
        options = facet.get('options', {})
        sqs = sqs.facet(facet['field'], **options)
    for facet in settings.OSCAR_SEARCH_FACETS['queries'].values():
        for query in facet['queries']:
            sqs = sqs.query_facet(facet['field'], query[1])
    return sqs
