import hmac
import json
import requests
import hashlib
import urllib3
from urllib3 import response

class Momo:
    def __init__(self,request_id,store_id,amount,order_id,order_info,extra_data,secret_key,access_key,partner_code,notify_url,return_url,momo_url):
        self.request_id = request_id
        self.store_id = store_id
        self.amount = amount
        self.order_id = order_id
        self.order_info = order_info
        self.extra_data = extra_data
        self.access_key = access_key
        self.partner_code = partner_code
        self.notify_url = notify_url
        self.return_url = return_url
        self.secret_key = secret_key
        self.request_type = "captureMoMoWallet"
        self.lang = "en"
        self.momo_url = momo_url
    
    def create_signature_data_string(self):
        rawSignature = "partnerCode="+self.partner_code+"&accessKey="+self.access_key+"&requestId="+self.request_id+"&amount="+str(self.amount)+"&orderId="+self.order_id+"&orderInfo="+self.order_info+"&returnUrl="+self.return_url+"&notifyUrl="+self.notify_url+"&extraData="+self.extra_data 
       
        return rawSignature.encode("utf-8")

    def create_signature(self):
        h = hmac.new( self.secret_key.encode("utf-8"), self.create_signature_data_string(), hashlib.sha256 )
        self.signature = h.hexdigest()

    def create_json(self):
        data = {
            "accessKey":self.access_key,
            "partnerCode":self.partner_code,
            "requestId":self.request_id,
            "amount":str(self.amount),
            "orderId":self.order_id,
            "orderInfo":self.order_info,
            "returnUrl":self.return_url,
            "notifyUrl":self.notify_url,
            "lang":self.lang,
            "extraData":self.extra_data,
            "requestType":self.request_type,
            "signature":self.signature
        }
        return json.dumps(data)

    def get_payment_url(self):
        request = requests.post(self.momo_url,data=self.create_json())
        print(request.json())
        return request.json()["payUrl"]

