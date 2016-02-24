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

def getRegionFromUrl(url):
#DetailPageURL
    urlExtension = url[18:21]

    if urlExtension == 'fr/':
        return 'fr'
    elif urlExtension == 'co.':
        if url[18:23] == 'co.uk':
            return 'uk'
        elif url[18:23] == 'co.jp':
            return 'jp'  
    elif urlExtension == 'com':
        return 'us'
    elif urlExtension == 'it/':
        return 'it'
    elif urlExtension == 'es/':
        return 'es'
    elif urlExtension == 'au/':
        return 'au'
    elif urlExtension == 'br/':
        return 'br'
    elif urlExtension == 'ca/':
        return 'ca'
    elif urlExtension == 'cn/':
        return 'cn'
    elif urlExtension == 'de/':
        return 'de'
    elif urlExtension == 'in/':
        return 'in'
    elif urlExtension == 'mx/':
        return 'mx'
    elif urlExtension == 'nl/':
        return 'nl'
        
    return 'unknown'



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

    listed = True
    try:
        api = API(locale='us')
        products = api.item_search('All', Keywords=search_text, paginate=False, ResponseGroup="ItemIds, ItemAttributes, Images, OfferSummary, Offers")
        
        niceProducts = []
        ASINList = []
  
        
        for product in products.Items.Item:
            try:
                niceProduct = Product()
                niceProduct.title = product.ItemAttributes.Title
                niceProduct.ASIN = product.ASIN.text
                ASINList.append(niceProduct.ASIN)
                
                niceProduct.imageUrl = product.MediumImage.URL
                
                
                #try:
                #    niceProduct.newPrice = float(product.OfferSummary.LowestNewPrice.Amount)/100
                #    niceProduct.newFormattedPrice = product.OfferSummary.LowestNewPrice.FormattedPrice
                #    niceProduct.newPriceCurrency = product.OfferSummary.LowestNewPrice.CurrencyCode
                #except:
                #    pass
                
                
                    
                try:
                    niceProduct.usedPrice = float(product.OfferSummary.LowestUsedPrice.Amount)/100
                    niceProduct.usedFormattedPrice = product.OfferSummary.LowestUsedPrice.FormattedPrice
                    niceProduct.usedPriceCurrency = product.OfferSummary.LowestUsedPrice.CurrencyCode
                except:
                    pass
                    
                niceProduct.type = product.ItemAttributes.ProductGroup
                niceProduct.region =  getRegionFromUrl(product.DetailPageURL.text).upper() #product.ItemAttributes.RegionCode
                niceProduct.model = product.ItemAttributes.Model
                niceProducts.append(niceProduct)
                if not listed:
                    print(objectify.dump(product))
                    listed = True
            except:
                pass
                #not a product
                
        res = api.item_lookup(*ASINList, MerchantId='Amazon', ResponseGroup = 'Offers')
        
        i = 0
        listed = False
        
        for amazonProduct in res.Items.Item:
            print 'new amazon offer for ASIN : ', amazonProduct.ASIN
            print '#########################################'
            #print objectify.dump(amazonProduct)
            try:
                #print 'not void!'
                #for offer in amazonProduct.Offers:
                print objectify.dump(amazonProduct)
                niceProducts[i].newPrice = float(amazonProduct.OfferSummary.LowestNewPrice.Amount)/100
                niceProducts[i].newFormattedPrice = amazonProduct.OfferSummary.LowestNewPrice.FormattedPrice
                niceProducts[i].newPriceCurrency = amazonProduct.OfferSummary.LowestNewPrice.CurrencyCode
                print 'price is : ', float(amazonProduct.OfferSummary.LowestNewPrice.Amount)/100
                
            except Exception as inst:
                print inst        
            #if not listed:
            #        print(objectify.dump(amazonProduct))
            #        listed = True
            #try:
            ##    print 'set price : ', i, ', ASIN : ', amazonProduct.ASIN
            ##    niceProducts[i].newPrice = float(amazonProduct.ItemAttributes.ListPrice.Amount)/100
            ##    niceProducts[i].newFormattedPrice = amazonProduct.ItemAttributes.ListPrice.FormattedPrice
            ##    niceProducts[i].newPriceCurrency = amazonProduct.ItemAttributes.ListPrice.CurrencyCode
            ##    print 'ok price for : ', i
            ##except:
            #    pass
            i+=1
               

    except errors.AWSError, e:
        print 'Amazon complained about yout request!'
        print e.code
        print e.msg
        return e.msg
    
    return render_template('search.html', search_text = request.args['q'], region = request.args['region'], products = niceProducts)
    

        
if __name__ == '__main__':
    app.secret_key = 'ssssshhhhh'
    app.run(debug=True)
    