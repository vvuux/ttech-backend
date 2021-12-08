from django.shortcuts import render
from django.views.generic.base import TemplateView,View

# Create your views here.

class MomoPaymentReturn(TemplateView):
    template_name = "project/momo-payment-return.html"

    # def get(self,request,*args,**kwargs):
    #     input = request.GET
    #     print("Input: ",input)
    #     print("kwargs: ",self.kwargs)
    #     # order_id = input["orderId"]
    #     # request_id = input["requestId"]
    #     # amount = input["amount"]
    #     # order_info = input["orderInfo"]
    #     # transId = input["transId"]
    #     # message = input["message"]
    #     # errorCode = input["errorCode"]
    #     # signature = input["signature"]
    #     # return render(self.request,self.template_name,context={
    #     #     "order_id":order_id,
    #     #     "amount":amount,
    #     #     "order_info":order_info,
    #     #     "trans_id":transId,
    #     #     "message":message,
    #     # })
    #     return render(self.request,self.template_name)

class NotifyUrl(View):
    def post(self,*args,**kwargs):
        result = self.request.POST
        partner_code = result["partnerCode"]
        request_id = result["requestId"]
        order_id = result["orderId"]
        result_code = result["resultCode"]
        message = result["message"]
        response_time = result["responseTime"]
        extra_data = result["extraData"]
        signature = result["signature"]
    
