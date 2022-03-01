# Django Oscar E-Commerce Framework Demo

## Description
Oscar is an e-commerce framework for Django designed for building domain-driven sites. In this demo, some features have been customized which are mentioned below:

- Filtering through attributes of product using haystack with solr as search backend
- Add to cart button in wishlist page to directly add product from wishlists page. Also, notify me button in case product is out of stock.
- Creating shared wishlist and adding users in shared wishlist. On adding users, mail is sent to user with link, using which they can see the wishlist shared with him.
- Owner can also remove users from shared wishlist, after which user cannot no longer access shared wishlist page.
- Mails are sent using celery

## Initial Setup
Install [oscar](https://django-oscar.readthedocs.io/en/stable/internals/getting_started.html) and its dependencies

Create a superuser 
```sh
./manage.py createsuperuser
```

You will have oscar running at http://localhost:8000
As of now, you wont be having any data, so will have to configure the catalogue from dashboard

Configure the catalogue from dashboard
- Catalog --- > Product Types --- > Create
- Catalog --- > Product Types --- > Product Attributes  --- > Create
- Catalog --- > Categories  --- > Create
- Fulfillment --- > Partners  --- > Create
- Catalog --- > Product  --- > Create

## Custom filtering

We can use oscar to filter products based on various search facets. For which, we will have to use search backend other than haystack's simple backend. In this demo, we have used Apache Solr, officially supported by Django Oscar.
Fields that are custom to application like product attributes are not by default indexed by oscar.

For that, some changes have to be done as mentioned below :
1. Setup [Solr](https://django-oscar.readthedocs.io/en/3.1/howto/how_to_setup_solr.html) with Django Oscar
2. Add below in settings.py:
    ```sh
    OSCAR_SEARCH_FACETS = {
        'fields': OrderedDict([
            ('product_class', {'name': _('Type'), 'field': 'product_class'}),
            ('rating', {'name': _('Rating'), 'field': 'rating'}),
        ]),
        'queries': OrderedDict([
            ('price_range',
             {
                 'name': _('Price range'),
                 'field': 'price',
                 'queries': [
                     # This is a list of (name, query) tuples where the name will
                     # be displayed on the front-end.
                     (_('0 to 20'), '[0 TO 20]'),
                     (_('20 to 40'), '[20 TO 40]'),
                     (_('40 to 60'), '[40 TO 60]'),
                     (_('60+'), '[60 TO *]'),
                 ]
             }),
        ]),
    }
    ```
    Now, you can see filter dropdown in catalogue page in oscar.


3. For adding custom filtering of product attributes, fork search app using below command :
    ```sh 
    python manage.py oscar_fork_app search ecommerce_apps
    ```
    In this demo, we have stored all forked apps in ecommerce_apps directory.

    
4. As product attributes are dynamic we have added dynamic facets in search_indexes.py file identified by suffix '_s'. Changes have been made in following files for dynamic facets which you can find in forked search app
    - search_handlers.py 
    - search_indexes.py (for adding dynamic facets)
    - facets.py (to show dynamic facets only when categories are selected)

    Also, replace below line in munge_field_facet function in facets.py
    ```sh
    field_name = '%s_exact' % facet['field']
    ```
    with
    ```sh
    field_name = '%s_exact' % facet['field'] if "_s" not in facet["field"] else facet["field"]
    ```

5. You will have to rebuild index using following command:
    ```sh
    python manage.py rebuild_index
    ```
    Once, all products are indexed properly, you can see filters on selection of category on catalogue page
    

## Shared Wishlists

> Customer and wishlists app have been forked inside ecommerce_apps folder for shared wishlists functionality.