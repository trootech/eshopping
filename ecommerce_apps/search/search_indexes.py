from oscar.apps.search.search_indexes import ProductIndex
from oscar.core.loading import get_class

# Load default strategy (without a user/request)
is_solr_supported = get_class('search.features', 'is_solr_supported')


class ProductIndex(ProductIndex):

    def prepare(self, obj):
        """
        This method is overridden to include dynamic facets that are of product attributes
        "_s" is appended to indicate that facet field is dynamic otherwise it will throw field not defined error
        """
        prepared_data = super().prepare(obj)
        if is_solr_supported():
            attribute_values = obj.attribute_values.all()
            if len(attribute_values) > 0:
                dynamic_dict = {}
            for attribute_value in attribute_values:
                dynamic_dict.update({attribute_value.attribute.name: attribute_value.value})

            for key, value in dynamic_dict.items():
                if not key + "_s" in prepared_data.keys():
                    prepared_data[key.lower() + "_s"] = value
                else:
                    prepared_data[key.lower() + "_s"].append(value)
        return prepared_data
