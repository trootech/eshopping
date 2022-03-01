from . import facets
from oscar.apps.search.search_handlers import SearchHandler as AbstractSearchHandler


class SearchHandler(AbstractSearchHandler):

    def get_search_queryset(self):
        """
        Returns the search queryset that is used as a base for the search.

        This method is overridden as dynamic attributes as facets are to be shown category-wise,
        so we need to pass categories when base search queryset is created
        """
        sqs = facets.base_sqs(self.categories)
        if self.model_whitelist:
            # Limit queryset to specified list of models
            sqs = sqs.models(*self.model_whitelist)
        return sqs
