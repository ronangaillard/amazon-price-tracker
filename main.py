from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import re
import os.path
import sqlite3
from amazon.api import AmazonAPI    
from amazonproduct import API, errors
from lxml import objectify



DATABASE = 'database.db'

app = Flask(__name__)
app.config.from_object(__name__)

class Product:
    """An amazon product"""
    title = ""
    ASIN=""
    imageUrl=""
    newPrice=""
    newFormattedPrice=""
    newPriceCurrency=""
    usedPrice=""
    usedFormattedPrice=""
    usedPriceCurrency=""
    thirdPartyNewPrice=""
    thirdPartyNewFormattedPrice=""
    thirdPartyNewPriceCurrency=""
    currency=""
    type=""
    def f(self):
        return 'hello world'



#Connects to the sqlite database
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
    
#Database functions
@app.before_request
def before_request():
	g.db=connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g,'db',None)
	if db is not None:
		db.close()


#Front End Routes
@app.route('/')
def entry_point():
    return render_template('index.html')
    
@app.route('/search', methods=['GET'])
def search():
    print "hello"
    search_text = request.args['q'] 
    region = request.args['region']

    listed = False
    try:
        api = API(locale='fr')
        products = api.item_search('All', Keywords=search_text, paginate=False, ResponseGroup="ItemIds, ItemAttributes, Images, OfferSummary")
        
        niceProducts = []
  
        
        for product in products.Items.Item:
            try:
                niceProduct = Product()
                niceProduct.title = product.ItemAttributes.Title
                niceProduct.ASIN = product.ASIN.text
                niceProduct.imageUrl = product.MediumImage.URL
                try:
                    niceProduct.newPrice = float(product.OfferSummary.LowestNewPrice.Amount)/100
                    niceProduct.newFormattedPrice = product.OfferSummary.LowestNewPrice.FormattedPrice
                    niceProduct.newPriceCurrency = product.OfferSummary.LowestNewPrice.CurrencyCode
                except:
                    pass
                    
                try:
                    niceProduct.usedPrice = float(product.OfferSummary.LowestUsedPrice.Amount)/100
                    niceProduct.usedFormattedPrice = product.OfferSummary.LowestUsedPrice.FormattedPrice
                    niceProduct.usedPriceCurrency = product.OfferSummary.LowestUsedPrice.CurrencyCode
                except:
                    pass
                    
                niceProduct.type = product.ItemAttributes.ProductGroup
                try:
                    niceProduct.region =  products.region #product.ItemAttributes.RegionCode
                except:
                    niceProduct.region = "?"
                niceProduct.model = product.ItemAttributes.Model
                niceProducts.append(niceProduct)
                if not listed:
                    print(objectify.dump(product))
                    listed = True
            except:
                pass
                #not a product

    except errors.AWSError, e:
        print 'Amazon complained about yout request!'
        print e.code
        print e.msg
        return e.msg
    
    return render_template('search.html', search_text = request.args['q'], region = request.args['region'], products = niceProducts)
    

        
if __name__ == '__main__':
    app.secret_key = 'ssssshhhhh'
    app.run(debug=True)
    