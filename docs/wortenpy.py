# http://docs.python-requests.org/en/master/
from requests import get
# https://beautiful-soup-4.readthedocs.io/en/latest/
from bs4 import BeautifulSoup
# Used to serialize dictionaries into JSON objects
import json
# Used for encoding the URLs for the GET requests
import urllib.parse
# A single dictionary with the product's characteristics\
# translated (portuguese -> english)
from wortenpy_translations import translations


class Worten():
    '''Class for connecting to Worten and retrieving products from \
queries.


    Attributes
    ----------
    endpoint : str 
        The target website (worten.pt in this case).
    hitsPerPage : str
        The number of results to be shown per page.
    page : str
        The page of results to request.
    query : str
        The query search term(s).
    query_soup : bs4.BeautifulSoup
        A BeautifulSoup object holding the the source code for a \
page of query results.
    retrived_prods : list
        A list of items where each item is the portion of the \
results page's HTML source code relative to a product result.
    sortBy : str
        The sorting order for the query results.
    total_num_prods_found : int
        Number of product results for the query.
    

    Methods
    -------
    connected()
        Test if the connection to Worten was successful.
    make_query(tags, **kwargs)
        Make a text query for products.
    get_prods(num_prods)
        Retrieve the first num_prods products from the \
query results, relative to the current page of results.
    get_prods_found(prods)
        Return a dictionary with mappings of product \
names to the URL of the product's page.
    get_prod_source()
        Get the BeautifulSoup object with the source \
code of the current page of the query's results.
    query_params()
        Returns a dictionary with information about the \
query parameters available to make text queries to Worten.
    '''

    # Connect to worten
    def __init__(self):
        '''
        Initialize the object by making a GET request \
to Worten.

        Parameters
        ----------
        None   
        '''

        # Make a GET request to Worten, i.e., connect to it
        self.endpoint = get('https://www.worten.pt')

    def __help__(self):
        '''
        Return the class' docstring.

        Parameters
        ----------
        None
        
        Returns
        -------
        str
            The class' docstring.
        '''

        return Worten.__doc__

    # Test if connection was successful
    def connected(self):
        '''
        Test if the connection to Worten was successfully
        established. In other words, we are testing if the
        request's status code is in the 200's.

        Parameters
        ----------
        None
        
        Returns
        -------
        bool
            Returns True if the connection was successful, else False.
        '''

        # Test if the request's status code is in the 200's, that is,\
        # between 200 and 299, inclusive
        return (self.endpoint.status_code // 200) == 1

    # Make a query
    def make_query(self, tags, **kwargs):
        '''
        Make a query to Worten, that is, search for products.

        Parameters for the query, except for the tags, must be \
passed as keyword arguments, with string values. For example: 
        make_query("god of war", sortBy="name", hitsPerPage="12", page="2")
        
        When the parameters are passed, sortBy defaults to \
"relevance", hitsPerPage to "24" and page to "1".
        
        For more information about the parameters, call the \
query_params method.
        
        Parameters
        ----------
        tags : str
            The string containing the tags for the query.
        sortBy : str, optional
            The sorting order for the query results.
        hitsPerPage : str, optional
            The number of results to be shown per page.
        page : str, optional
            The page of results to request.

        Returns
        -------
        query_soup : bs4.BeautifulSoup
            A BeautifulSoup object holding the the source code for \
the requested page of query results.

        Raises
        ------
        NameError
            Raised if the user requested a page of results that \
doesn't exist.
        '''

        # Sort the results by
        self.sortBy = kwargs['sortBy'] if 'sortBy' in kwargs else 'relevance'
        # Number of results per page
        self.hitsPerPage = kwargs['hitsPerPage'] if 'hitsPerPage' in kwargs else '24'
        # The page of results to request
        self.page = kwargs['page'] if 'page' in kwargs else '1'
        # Format the passed 'tags' to be used as query parameters, in case there's multiple words in it
        # We save the tags in a class attribute for use in a separate class method
        self.query = tags
        query_url = 'https://www.worten.pt/search?' + urllib.parse.urlencode({'sortBy':self.sortBy, 'hitsPerPage':self.hitsPerPage, 'page':self.page, 'query':self.query})
        query_endpoint = get(query_url)
        self.query_soup = BeautifulSoup(query_endpoint.content, 'lxml', from_encoding="iso-8895-15")
        try:
            # The number of products found with the query
            self.total_num_prods_found = int(self.query_soup.find('span', 
                class_='w-filters__element w-filters__results show-for-medium').text.split()[-1])
            return self.query_soup
        except:
            # If it wasn't possible to find how many results the query has, then it means the\
            # user requested a page of results that doesn't exist, thus raise an exception
            raise NameError('The query doesn\'t have enough pages of results for your request.')
    
    # Get source code for each product found    
    def get_prods(self, num_prods):
        '''
        Retrieve the first num_prods products from the query results \
(relative to the requested page not the first page of results).
        
        Parameters
        ----------
        num_prods : int
            The first num_prods products will be retrieved.
        
        Returns
        -------
        retrieved_prods : list
            A list of all the retrived products (rather, a list where \
each item is the portion of the results page's source code that's \
relative to the retrieved products).
        '''

        # List to hold the scraped products
        self.retrived_prods = []
        # The difference between the number of requested products\
        # and how many have been scraped
        products_left = num_prods - len(self.retrived_prods)
                
        # Use this variable instead of the class attribute, so we keep the\
        # initial value
        page = str(self.page)
        # Calculate the number of page results
        last_page = (self.total_num_prods_found // int(self.hitsPerPage)) + 1

        # Scrape products from the current page, and if it isn't enough,\
        # move on to the next page while we don't have enough scraped\
        # products and there's more pages
        while products_left:
            
            # Try to scrape a page of query results
            try:
                # Create a URL to request a page of results
                query_url_temp = 'https://www.worten.pt/search?' +\
                    urllib.parse.urlencode({
                        'sortBy':self.sortBy, 
                        'hitsPerPage':self.hitsPerPage, 
                        'page':self.page, 
                        'query':self.query
                    }
                )
                # query_endpoint = get(f'https://www.worten.pt/search?sortBy={self.sortBy}&hitsPerPage={self.hitsPerPage}&page={page}&query={self.query}')
                query_endpoint = get(query_url_temp)
                query_soup_temp = BeautifulSoup(query_endpoint.content, 'lxml', from_encoding="iso-8895-15")
            # If something goes wrong with scraping the next page, assume there's\
            # no more pages, and break out of the loop (we'll return as many\
            # products as we currently have)
            except:
                break
            
            # Find all products in the current page
            prods = query_soup_temp.find_all('div', class_='w-product qa-product__content--')

            # Now loop through the page of results to scrape more products
            for i in range(products_left):
                # Try to scrape another product and append it to the list
                try:
                    self.retrived_prods.append(prods[i])
                # If something goes wrong, break out of the loop and\
                # return as many products as we currently have
                except:
                    break
            
            # After scraping this page of results, update the number of\
            # scraped products, rather, the number of products to scrape
            # left
            products_left = num_prods - len(self.retrived_prods)
            # And move to the next page
            page = str(int(page)+1)
            
            # If we are already at the last page of results, break out\
            # of the loop and return the scraped products we currently\
            # have
            if int(page) > last_page:
                break
                    
        return self.retrived_prods
    
    # Dictionary with pairs prod_name: prod_url
    def get_prods_found(self, prods):
        '''
        Return a dictionary with mappings of the products' names found \
to the the URL of its pages.

        Parameters
        ----------
        prods : list
            A list of snippets of HTML from the scraped source code of a \
page of results, where each snippet pertains to a specific result in a \
query.
        
        Returns
        -------
        dict
            A dictionary with the mapping of product names to its pages' \
URLs.
        '''

        # prod_name = snippet.find('h3', class_='w-product__title').text
        # prod_page_url = 'https://www.worten.pt' + snippet.find('a', class_='w-product__url qa-product-block__product-image--')['href']
        # {prod_name: prod_page_url}
        return {snippet.find('h3', class_='w-product__title').text: \
            'https://www.worten.pt' + snippet.find('a', class_='w-product__url qa-product-block__product-image--')['href'] \
            for snippet in prods}
    
    # Get query results page source code (current page)
    def get_prod_source(self):
        '''
        Get the BeautifulSoup object with the source code of the current \
page of query results.
        
        Parameters
        ----------
        None

        Returns
        -------
        requests.models.Response
            The source code of the page.
        '''

        return self.query_soup

    # Explanation about the query parameters
    def query_params(self):
        '''
        Returns a dictionary with information about each query parameter. \
        
        The value for each pair is a tuple where the first item is a brief \
explanation of the parameter, the second item is a list of the possible \
values for each parameter and the third item is the default value.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            The dictionary with the parameters' informations.
        '''

        return {
            'sortBy': (
                'How to sort the results', 
                ['relevance', 'name', 'priceAsc', 'priceDesc', 'brand'], 
                'relevance'
            ),

            'hitsPerPage': (
                'The number of results to show per page of results', 
                ['12', '24', '48'], 
                '24'
            ),

            'page': (
                'The "landing page" of results of the query', 
                ['An integer value'], 
                '1'
            )
        }


class Product():
    '''Class for interacting with a single product's page.
    
    Attributes
    ----------
    all_info : dict
        Dictionary with all the information scraped about a \
product.
    json_format : dict
        A string to hold a JSON object with the product's \
main information.
    more_info : bs4.element.Tag
        The part of the product page's source code about its \
detailed information.
    num_pics : int
        Number of pictures available for the product.
    og_price : float
        Original price for the product (in case it's on sale).
    pictures : list
        A list with the URLs for the available product pictures.
    price_unit : str
        Unit used for the product price.
    prod_avail : str
        The product availability status.
    prod_brand : str
        The product's brand.
    prod_cat : str)
        The product category.
    prod_color : str
        The color of the product.
    prod_desc : str
        The product description.
    prod_dimensions : str
        Dimensions of the product.
    prod_discount : float
        Discount percentage (in case the product is on sale).
    prod_ean : str
        The product's European Article Number, also known as \
International Article Number.
    prod_link : str
        Product page's URL.
    prod_model : str
        The product model.
    prod_name : str
        Name of the product.
    prod_price : float
        The product's current price.
    prod_ref : str
        The product internal reference.
    prod_weight : str
        The product weight.
    query_prod : requests.models.Response
        The response for the GET request of a product's page.
    query_prod_soup : bs4.BeautifulSoup
        BeautifulSoup object for a product's page.
    xml_format : str
        A string to hold a XML with the product's main information.

    Methods
    -------
    connected()
        Test if the connection to the product page was successful.
    get_prod_source()
        Get the source code of the product page.
    on_sale()
        Check if the product is on sale.
    get_main_info(*args)
        Get a Python dictionary and/or XML string and/or JSON object \
with the main informations about the product.
    main_info_types()
        Returns a dictionary with the main information types' names.
    prod_info_types()
        Returns a dictionary with the name of all the types of \
information.
    get_all_info(*args)
        Get a Python dictionary and/or XML string and/or JSON object \
with all the informations about the product.
    specific_info(*args)
        Get a Python dictionary with only the types of information \
passed as arguments to the function call.
    '''

    def __init__(self, product):
        '''
        Make a GET request for the page of a given product.
        
        Parameters
        ----------
        product : bs4.element.Tag
            The portion of the source code of a page of results from \
a text query made on Worten's website, relative to a single product.
        '''

        # A single dictionary with all the informations about this\
        # product to facilitate the work in other methods. Each\
        # information is added to the dictionary after being scraped
        self.all_info = {}

        # Connect to the product's page through a GET request
        try:
            self.prod_link = 'https://www.worten.pt' + product.div.a['href']
            self.all_info['prod_link'] = self.prod_link
            self.query_prod = get(self.prod_link)
        # If something goes wrong, return prematurely
        except:
            return None

        # After connecting to the product's page, set a number of attributes for the object
        try:
            # Create a BeautifulSoup object for the source code of the product's page
            self.query_prod_soup = BeautifulSoup(self.query_prod.content, 'lxml', from_encoding="iso-8895-15")
            # Product detailed info
            self.more_info = self.query_prod_soup.find('div', class_='w-product-details__wrapper').div
        # Return prematurely if it was not possible to create a BS object or scrape\
        # the product's detailed info
        except:
            return None
        
        # After the "set-up", scrape the main informations about the product\
        # and store them as attributes for the object
        
        # Product availability
        # If there's a <div> for available products, it means the product is available
        if self.query_prod_soup.find('div', class_='w-product__availability-title'):
            self.prod_avail = 'Available'
        # If there's a <div> for unavailable products, it means the product is not available
        elif self.query_prod_soup.find('div', class_='w-product__unavailability-title'):
            self.prod_avail = 'Not Available'            
        # If neither of the two <div>s exist, the product is available only by pre-order
        else:
            self.prod_avail = 'Pre-Order'

        # For the following types of information, we first try to scrape them inside the try\
        # block. If something goes wrong or the information just doesn't exist in the page,
        # inside the except block we save that information with a value of None.
        
        # After setting a value for the information, we add it to the dictionary that contains\
        # all information scraped about the product

        # Product name
        try:
            self.prod_name = self.more_info.header.h2.find('span', class_='w-section__product').text.strip()
        except:
            self.prod_name = None
        self.all_info['prod_name'] = self.prod_name

        # Product category (a single <ul> contains one or more <li> tags, each containing <a> tags\
        # that contain the text we want, the categories)
        try:
            self.prod_cat = self.query_prod_soup.find('ul', class_='w-breadcrumbs breadcrumbs').find_all('li')[-1].a.text.strip()
        except:
            self.prod_cat = None
        self.all_info['prod_cat'] = self.prod_cat

        # Product current price (if it's on sale, scrapes the discounted price)
        try:
            self.prod_price = self.query_prod_soup.find('span', class_='w-product__price__current')['content']
        except:
            self.prod_price = None
        self.all_info['prod_price'] = self.prod_price

        # Unit used for the prices
        self.price_unit = 'EURO'
        self.all_info['price_unit'] = self.price_unit

        # Check if the product's current price is a discounted price and if it\
        # is scrape the original price and calculate the discount percentage

        # If it is discounted, there will be a specific <span> tag in the HTML
        if self.query_prod_soup.find('span', class_='w-product__price__old'):
            # Original price (don't include the euro symbol)
            self.prod_og_price = self.query_prod_soup.find('span', class_='w-product__price__old').text.strip()[1:]
            # Original price converted to float
            float_og_price = float(self.prod_og_price.replace(',', '.'))
            # Price on sale converted to float
            float_sale_price = float(self.prod_price.replace(',', '.'))
            # Calculate the discount percentage, rounded to 1 decimal point precision
            self.prod_discount = str(100 - round((float_sale_price * 100) / float_og_price, 1)) + '%'
        
        # If the product is not on sale, the attributes relative to discounts \
        # have a value of None
        else:
            self.prod_og_price = None
            self.prod_discount = None

        self.all_info['prod_og_price'] = self.prod_og_price
        self.all_info['prod_discount'] = self.prod_discount


        # Product pictures' links
        # If this <div> is found, run the following block of code.
        # This <div> is only present when the product has 5 or \
        # less pictures
        # if self.query_prod_soup.find('div', class_='swiper-container w-product-gallery__thumbnails swiper__off').find_all('div', class_='swiper-slide'):
        if self.query_prod_soup.find('div', class_='swiper-container w-product-gallery__thumbnails swiper__off'):
            pics = self.query_prod_soup.find('div', class_='swiper-container w-product-gallery__thumbnails swiper__off')\
            .find_all('div', class_='swiper-slide')
            self.pictures = ['https://www.worten.pt'+pic.a.img["src"] for pic in pics]
        
        # If the above <div> is not found, try to find this <div>\
        # instead.
        # This <div> only exists when a product has more than 5 pictures
        # elif self.query_prod_soup.find('div', class_='swiper-wrapper').find_all('div'):
        elif self.query_prod_soup.find('div', class_='swiper-wrapper'):            
            pics = self.query_prod_soup.find('div', class_='swiper-wrapper').find_all('div')
            self.pictures = ['https://www.worten.pt'+pic.a.img["src"] for pic in pics]

        # If neither of the above <div> are found, assume the product\
        # doesn't have pictures
        else:
            self.pictures = []
        self.all_info['prod_pictures'] = self.pictures

        # Number of product pictures
        self.num_pics = len(self.pictures)

        # Product description
        try:
            self.prod_desc = self.query_prod_soup.find('div', class_='w-section__wrapper__content').find_all('p')[1].text.strip()
        except:
            self.prod_desc = None
        self.all_info['prod_desc'] = self.prod_desc
        
        # Left column info (Usually "Referências", "Características Físicas" and "Mais Informações")
        left_col = self.more_info.find('div', class_='w-product-details__column w-product-details__moreinfo show-for-medium')
        # Scrapes the titles of each list of aspects in the left column
        l_col_titles = [col.text.strip() for col in left_col.find_all('p')]
        # Scrapes the <ul> tags from the previous section, that is, just the lines\
        # of the list without the title
        l_info_ULs = [col for col in left_col.find_all('ul')]
        # Scrapes <li> tags nested in the previous <ul> tags, that is, each <li>\
        # corresponds to a line of the list of information
        l_info_LIs = [col.find_all('li') for col in l_info_ULs]

        # Right column info (includes even more specific information)
        right_col = self.more_info.find('div', class_='w-product-details__column')
        # Scrapes the titles of each list of aspects in the left column
        r_col_titles = [col.text.strip() for col in right_col.find_all('p')]
        # Scrapes the <ul> tags from the previous section, that is, just the lines\
        # of the list without the title
        r_info_ULs = [col for col in right_col.find_all('ul')]
        # Scrapes <li> tags nested in the previous <ul> tags, that is, each <li>\
        # corresponds to a line of the list of information
        r_info_LIs = [col.find_all('li') for col in r_info_ULs]

        # Product internal reference
        try:
            self.prod_ref = l_info_ULs[0].li.find('span', class_='details-value').text.strip()
        except:
            self.prod_ref = None
        self.all_info['prod_ref'] = self.prod_ref

        # Initialize strings to hold information about these aspects of the product.
        # They begin as empty strings, so that if they are still empty after trying\
        # to scrape them, it is assumed the information is not available
        self.prod_ean = ''
        self.prod_brand = ''
        self.prod_model = ''
        self.prod_weight = ''
        self.prod_dimensions = ''
        self.prod_color = ''

        # Loop through the <li> elements of the left column, looking for the desired\
        # information.
        # Note we need a nested for loop, since in the outer loop we loop through the\
        # <li> tags stored in the l_info_LIs list, that is, we are simply looping\ 
        # through that list in the outer loop. In the nested loop, we loop through\
        # each <li> of each of those iterables (which are the lists of information\
        # from the left column of the product specifications), that is, in the nested\
        # loop we loop through the lists inside of the bigger list
        for lst in l_info_LIs:
            for li in lst:
                # Product EAN (European Article Number) a.k.a International Article Number (IAN)
                try:
                    if 'EAN' in li.find('span', class_='details-label').text:
                        self.prod_ean = li.find('span', class_='details-value').text.strip()
                except:
                    self.prod_ean = None

                # Product brand
                try:
                    if 'Marca' in li.find('span', class_='details-label').text:
                        self.prod_brand = li.find('span', class_='details-value').text.strip()
                except:
                    self.prod_brand = None
                
                # Product model
                try:
                    if 'Modelo' in li.find('span', class_='details-label').text:
                        self.prod_model = li.find('span', class_='details-value').text.strip()
                except:
                    self.prod_model = None
                
                # Product weight
                try:
                    if 'Peso' in li.find('span', class_='details-label').text:
                        self.prod_weight = li.find('span', class_='details-value').text.strip() + ' kg'
                except:
                    self.prod_weight = None

                # Even though 'Altura', 'Largura' and 'Profundidade' (Height, Width, Depth) will\
                # all make a up a single Dimensions value, they need to be scraped separately
                try:
                    if 'Altura' in li.find('span', class_='details-label').text:
                        self.prod_dimensions += li.find('span', class_='details-value').text.strip() + '*'

                    if 'Largura' in li.find('span', class_='details-label').text:
                        self.prod_dimensions += li.find('span', class_='details-value').text.strip() + '*'

                    if 'Profundidade' in li.find('span', class_='details-label').text:
                        self.prod_dimensions += li.find('span', class_='details-value').text.strip() + ' cm'
                except:
                    self.prod_dimensions = None

                # Product color
                try:
                    if 'Cor' in li.find('span', class_='details-label').text:
                        self.prod_color = li.find('span', class_='details-value').text.strip()
                except:
                    self.prod_color = None

        # After trying to scrape information about these aspects, if the strings are\
        # still empty then just assume the information about said aspects is not\
        # available
        else:
            if not self.prod_ean:
                self.prod_ean = None
            if not self.prod_brand:
                self.prod_brand = None
            if not self.prod_model:
                self.prod_model = None
            if not self.prod_weight:
                self.prod_weight = None
            if not self.prod_dimensions:
                self.prod_dimensions = None
            if not self.prod_color:
                self.prod_color = None
        
        self.all_info['prod_ean'] = self.prod_ean
        self.all_info['prod_brand'] = self.prod_brand
        self.all_info['prod_model'] = self.prod_model
        self.all_info['prod_weight'] = self.prod_weight
        self.all_info['prod_dimensions'] = self.prod_dimensions

        # Scrape every information available in the left column of\
        # the product's detailed info
        # Loop through a list of <li> elements
        for lst in l_info_LIs:
            # Loop through the <li>s of the current list
            for li in lst:
                # Get the label of this <li>
                info_type = li.find('span', class_='details-label').text
                # If the label is on the translations dictionary, translate\
                # the label to english and save it along with the actual\
                # information
                if info_type in translations:
                    info_type_trans = translations[info_type]
                    self.all_info[info_type_trans] = li.find('span', class_='details-value').text.strip()

        # Scrape every information available in the right column of\
        # the product's detailed info
        # Loop through a list of <li> elements
        for lst in r_info_LIs:
            # Loop through the <li>s of the current list
            for li in lst:
                # Get the label of this <li>
                info_type = li.find('span', class_='details-label').text
                # If the label is on the translations dictionary,\
                # translate the label to english and save it along\
                # with the actual information
                if info_type in translations:
                    info_type_trans = translations[info_type]
                    self.all_info[info_type_trans] = li.find('span', class_='details-value').text.strip()

        # Dictionary to hold just the main information scraped about\
        # the product
        self.prod_main_info = {
            'prod_name': self.prod_name,
            'prod_page': self.prod_link,
            'prod_cat': self.prod_cat,
            'prod_price': self.prod_price,
            'prod_og_price': self.prod_og_price,
            'prod_discount': self.prod_discount,
            'prod_avail': self.prod_avail,
            'prod_pictures': self.pictures,
            'prod_desc': self.prod_desc,
            'prod_ean': self.prod_ean,
            'prod_brand': self.prod_brand,
            'prod_model': self.prod_brand,
            'prod_weight': self.prod_weight,
            'prod_dimensions': self.prod_dimensions,
            'prod_color': self.prod_color
        }

    
    def __help__(self):
        '''
        Return the class' docstring.

        Parameters
        ----------
        None
        
        Returns
        -------
        str
            The class' docstring.
        '''

        return Product.__doc__

    # Test if the connection was successful
    def connected(self):
        '''
        Test if the connection to the product page was \
successfully established. In other words, we are testing \
if the request's status code is in the 200's.

        Parameters
        ----------
        None
        
        Returns
        -------
        bool
            Returns True if the connection was successful, \
else False.
        '''

        # Test if the request's status code is in the 200's, that is,\
        # between 200 and 299, inclusive
        return self.query_prod.status_code//200 == 1

    # Get page source code
    def get_prod_source(self):
        '''
        Get the BeautifulSoup object with the source code \
of a single product's page.
        
        Parameters
        ----------
        None

        Returns
        -------
        requests.models.Response
            The source code of the product's page.
        '''

        return self.query_prod_soup
        
    # Test if the product is on sale
    def on_sale(self):
        '''
        Test if a product is on sale. It returns a \
Boolean value after checking if the product has an \
original price and a discount percentage.

        Parameters
        ----------
        None
        
        Returns
        -------
        bool
            True if the product's original price and \
discount percentage attributes are not None, else False.
        '''
        
        return bool(self.prod_og_price and self.prod_discount)

    # Get the product main informations in dict/xml/json
    def get_main_info(self, *args):
        '''
        Return the scraped main information of a \
product.

        This can be a dictionary, a formated string \
to be written to an .xml file and/or a JSON object. \
The returned formats are saved in a single dictionary.

        Parameters
        ----------
        dictionary : str, optional
            Indicates that the method should return \
the information in the form of a Python dictionary.
        xml : str, optional
            Indicates that the method should return \
a formated string, ready to be written to an .xml file.
        json : str, optional
            Indicates that the method should return a \
JSON object.

        Returns
        -------
        info_formats : dict
            A dict that holds between zero to three \
pairs, with the possible values for each pair being \
the product's main information in the three different \
formats.
        '''

        # List to hold the created formats
        info_formats = {}

        # Create the dictionary with the information
        if 'dictionary' in args:
            # Since the dictionary is created anyway in the\
            # __init__, just add it to info_formats
            info_formats['dictionary'] = self.prod_main_info
        
        # Format a string with the XML about the information
        if 'xml' in args:
            self.xml_format = '<?xml version="1.0" encoding="iso-8859-15" ?>'
            self.xml_format += f'\n<product reference="{self.prod_ref}" EAN="{self.prod_ean}" availability="{self.prod_avail}">'
            self.xml_format += f'\n\t<name>{self.prod_name}</name>'
            self.xml_format += f'\n\t<page href="{self.prod_link}"/>'
            self.xml_format += f'\n\t<category>{self.prod_cat}</category>'
            # Conditional clause for the 'on_sale' XML attribute
            if self.on_sale():
                self.xml_format += f'\n\t<price on_sale="Y" unit="EURO">{self.prod_price}</price>'
            else:
                self.xml_format += f'\n\t<price on_sale="N" unit="EURO">{self.prod_price}</price>'
            self.xml_format += f'\n\t<original_price discount="{self.prod_discount}" unit="EURO">{self.prod_og_price}</original_price>'            
            self.xml_format += f'\n\t<pictures>'
            for i in self.pictures:
                self.xml_format += f'\n\t\t<picture href="{i}"/>'
            self.xml_format += f'\n\t</pictures>'
            self.xml_format += f'\n\t<description>{self.prod_desc}</description>'
            self.xml_format += f'\n\t<more_info>'
            self.xml_format += f'\n\t\t<info type="BRAND">{self.prod_brand}</info>'
            self.xml_format += f'\n\t\t<info type="MODEL">{self.prod_model}</info>'
            self.xml_format += f'\n\t\t<info type="WEIGHT">{self.prod_weight}</info>'
            self.xml_format += f'\n\t\t<info type="DIMENSIONS">{self.prod_dimensions}</info>'
            self.xml_format += f'\n\t\t<info type="COLOR">{self.prod_color}</info>'
            self.xml_format += f'\n\t</more_info>'
            self.xml_format += f'\n</product>'
            
            info_formats['xml'] = self.xml_format
        
        # Create a dictionary with the information, then\
        # serialize it into a JSON object
        if 'json' in args:
            # Create the JSON object from the already\
            # existing dictionary
            self.json_format = json.dumps(self.prod_main_info, indent=4)
            info_formats['json'] = self.json_format

        return info_formats
    
    # Tuple with the main information types' names
    def main_info_types(self):
        '''
        Returns a tuple with all the types of \
information about a product that are considered \
as main types of information.

        Parameters
        ----------
        None
        
        Returns
        -------
        tuple
            The tuple with the main information \
types' names.
        '''
        
        return tuple([info_type for info_type in self.prod_main_info])

    # All the types of information a product can have  
    def prod_info_types(self):
        '''
        Return a sorted list with the different types of \
information that can be scraped about a product.
        
        These types can be passed as arguments in other \
methods to scrape specific informations about a product.

        Parameters
        ----------
        None
        
        Returns
        -------
        list
            An alphabetically sorted list with all the \
types of information.
        '''

        return sorted([translations[key] for key in translations])

    # Get all the scraped information
    def get_all_info(self, *args):
        '''
        Return all the scraped main information of a \
product.
        
        This can be a dictionary, a formated string \
to be written to an .xml file and/or a JSON object. \
The returned formats are saved in a single dictionary.

        Parameters
        ----------
        dictionary : str, optional
            Indicates that the method should return \
the information in the form of a Python dictionary.
        xml : str, optional
            Indicates that the method should return a \
formated string, ready to be written to an .xml file.
        json : str, optional
            Indicates that the method should return a \
JSON object.

        Returns:
        info_formats : dict
            A dict that holds between zero to three \
pairs, with the possible items being the product's \
information in the three different formats.
        '''

        # List to hold the created formats
        info_formats = {}

        # Create the dictionary with the information
        if 'dictionary' in args:
            # Since the dictionary is created anyway in the\
            # __init__, just add it to info_formats
            info_formats['dictionary'] = self.all_info
        
        # Format a string with the XML about the information
        if 'xml' in args:
            self.xml_format = '<?xml version="1.0" encoding="iso-8859-15" ?>'
            self.xml_format += f'\n<product reference="{self.prod_ref}" EAN="{self.prod_ean}" availability="{self.prod_avail}">'
            self.xml_format += f'\n\t<name>{self.prod_name}</name>'
            self.xml_format += f'\n\t<page href="{self.prod_link}"/>'
            self.xml_format += f'\n\t<category>{self.prod_cat}</category>'
            # Conditional clause for the 'on_sale' XML attribute
            if self.on_sale():
                self.xml_format += f'\n\t<price on_sale="Y" unit="EURO">{self.prod_price}</price>'
            else:
                self.xml_format += f'\n\t<price on_sale="N" unit="EURO">{self.prod_price}</price>'
            self.xml_format += f'\n\t<original_price discount="{self.prod_discount}" unit="EURO">{self.prod_og_price}</original_price>'            
            self.xml_format += f'\n\t<pictures>'
            for i in self.pictures:
                self.xml_format += f'\n\t\t<picture href="{i}"/>'
            self.xml_format += f'\n\t</pictures>'
            self.xml_format += f'\n\t<description>{self.prod_desc}</description>'
            self.xml_format += f'\n\t<more_info>'
            self.xml_format += f'\n\t\t<info type="BRAND">{self.prod_brand}</info>'
            self.xml_format += f'\n\t\t<info type="MODEL">{self.prod_model}</info>'
            self.xml_format += f'\n\t\t<info type="WEIGHT">{self.prod_weight}</info>'
            self.xml_format += f'\n\t\t<info type="DIMENSIONS">{self.prod_dimensions}</info>'
            self.xml_format += f'\n\t\t<info type="COLOR">{self.prod_color}</info>'
            for charac_type in self.all_info:
                self.xml_format += f'\n\t\t<info type="{charac_type}">{self.all_info[charac_type]}</info>'
            self.xml_format += f'\n\t</more_info>'
            self.xml_format += f'\n</product>'
            
            info_formats['xml'] = self.xml_format
        
        # Create a dictionary with the information, then\
        # serialize it into a JSON object
        if 'json' in args:
            # Create the JSON object from the already existing dictionary
            self.json_format = json.dumps(self.all_info, indent=4)
            info_formats['json'] = self.json_format

        return info_formats

    # Retrieve only specific information
    def specific_info(self, *args):
        '''
        Return only the information that was passed as \
an argument to the method call. If no argument was \
passed, return all of the "Extra Information" scraped.
        
        For a full list of supported arguments, call \
the prod_info_types() method.

        Parameters
        ----------
        list, optional
            A list of strings of the types of information \
to be returned as a dictionary.

        Returns:
        prod_extra_info : dict
            A dictionary with key-value pairs of the type \
info_type: value.
        '''

        # Dictionary to be returned
        prod_extra_info = {}

        # If no argument was passed, create a dictionary with\
        # all the information scraped about the product
        if not args:
            return self.all_info
        
        # If there were arguments the dictionary will contain\
        # only the required informations
        else:
            for arg in args:
                if arg in self.all_info:
                    prod_extra_info[arg] = self.all_info[arg]
                else:
                    prod_extra_info[arg] = 'Information not made available'
            return prod_extra_info




# The following are just examples of how to use the module
if __name__ == '__main__':
    # Core use for the module
    # 1- Connect to worten (Worten())
    # 2- Make a query (.make_query(tags, sortBy="", hitsPerPage="", page=""))
    # 3- Get product results (.get_prods(n))

    # 4- Create an object for a single product (Product(single_product))
    # 5- Create a dictionary/XML string/JSON object using the product's main\
    # information (.get_main_info('dictionary', 'xml', 'json'))
    # 6- Create a dictionary/XML string/JSON object using the all of the\
    # product's scraped information (.get_all_info('dictionary', 'xml', 'json'))


    # Tags for the query on worten.pt
    query_tags = 'spider man ps4'

    # Create an object for connecting to Worten 
    connect = Worten()
    # Test if the connection was successful
    print('Connected to Worten?', connect.connected())
    # Make a query using the tags defined
    # For a list of accepted values for the keyword arguments, please call\
    # the query_params() method
    connect.make_query(query_tags, sortBy="relevance", hitsPerPage="24", page="1")
    # Total number of results for the query
    print('Results found for the query:', connect.total_num_prods_found)
    # Retrieve the first n products from the query (starting from the\
    # current page).
    # This is a list of scraped products. Since the scraping was from the\
    # query results' page, each item of the list is a snippet of the page's\
    # source code, referring to a single product
    prods = connect.get_prods(13)
    # Number of retrieved products (depending on the number of results,\
    # the number of retrieved products may not be the same as the number\
    # of requested products)
    print('Number of scraped products:', len(prods)) 
    # Dictionary where each key-value pair corresponds to a scraped\
    # product's name and the URL to its page   
    prods_found_info = connect.get_prods_found(prods)
    # print('Products found:\n\t', prods_found_info)

    print()
    print()

    # Create an object for a single product
    # Retrieve the source code of a single product's page.
    # Here we are feeding the class with the HTML snippet of a single\
    # product from the query results page
    single_prod = Product(prods[0])
    # Test if we connected to the product page successfully
    print('Connected to the product page?', single_prod.connected())
    # Retrieve a BS4 object for the source code of the product's page
    single_prod_soup = single_prod.get_prod_source()
    # Create a dictionary, a XML-formated string and a JSON object with\
    # the scraped main information
    single_prod_info = single_prod.get_main_info('dictionary', 'xml', 'json')
    # Create a dictionary, a XML-formated string and a JSON object with\
    # all the scraped information
    single_prod_all_info = single_prod.get_all_info('dictionary', 'xml', 'json')
    # Now that we have a dictionary with the product's details, we can extract\
    # informations easily.
    # For a list of the main information types, please call the main_info_types() method
    # For a list of all the possible information types, please call the prod_info_types() method
    print('Product name:', single_prod_info['dictionary']['prod_name'])
    # Example for how to print the main information scraped
    print('Main information scraped:')
    for key in single_prod_info['dictionary']:
        print(f"\t{key}: {single_prod_info['dictionary'][key]}")
    print()
    # Example for how to print all the information scraped
    print('All information scraped:')
    for key in single_prod_all_info['dictionary']:
        print(f"\t{key}: {single_prod_all_info['dictionary'][key]}")
    # The on_sale() method verifies if a product is on sale or not and if it is,\
    # what is the discount percentage
    print('Product on sale?', single_prod.on_sale(), '\n')
    # Call the specific_info() method to obtain a dictionary with just specific\
    # information about a product. In the method call, pass the information types\
    # you want as arguments.
    # For a list of supported arguments, call the prod_info_types() method
    # print(single_prod.specific_info('model', 'prod_brand', 'prod_desc'))



    # Write the created XML using the main scraped information\
    # to a .xml file
    with open('XML_information.xml', 'w') as f:
        f.write(single_prod_info['xml'])

    # Write the created JSON using the main scraped information\
    # to a .json file
    with open('JSON_information.json', 'w') as f:
        f.write(single_prod_info['json'])

    # Write the created XML using all the scraped information\
    # to a .xml file
    with open('XML_all_information.xml', 'w') as f:
        f.write(single_prod_all_info['xml'])

    # Write the created JSON using all the scraped information\
    # to a .json file
    with open('JSON_all_information.json', 'w') as f:
        f.write(single_prod_all_info['json'])