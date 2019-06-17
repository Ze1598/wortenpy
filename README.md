# wortenpy
A programmatic interface to scrape products from worten.pt

I set off to create wortenpy so that it was possible to scrape products from worten.pt. This module allows the user to connect to the website, make a text query, with the option to modify the query parameters.
Then, from the page of query results, the user can scrape as many products as possible.
From those products, the user can create an object for each product and extract the product's informations. 
This extraction can be made into a Python dictionary, a string with XML ready to be written to a .xml file, or a JSON object (which can of course be written to a .json file).

Below is a step by step of the core functionalities for the module:

* Connect to worten (Worten());

* Make a query (.make_query(tags, sortBy="", hitsPerPage="", page=""));

* Get product results (.get_prods(n));

* Create an object for a single product (Product(single_product));

* Create a dictionary/XML string/JSON object using the product's main information (.get_main_info('dictionary', 'xml', 'json'));

* Create a dictionary/XML string/JSON object using the all of the product's scraped information (.get_all_info('dictionary', 'xml', 'json')).
	
	
The module is definitely open for changes in the future, specially for the translations. Even if the translations dictionary seems long, I only included the most common characteristics I found across the majority of categories available on the website.

### Update log:

* (august 11th 2018) Added initial Sphinx documentation.

* (june 17th 2019) Corrected some bugs from Worten's web page structure changing over time.

### External references:

* Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

* Requests: http://docs.python-requests.org/en/master/