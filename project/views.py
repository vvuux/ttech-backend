from django.http import request, response
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import ListView,DetailView
from django.http.response import JsonResponse,HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from datetime import datetime
from django.utils import timezone,dateparse
import hmac
import hashlib
from momo.momo import Momo

from vnpay.vnpay import vnpay
from project.models import ProjectChangeHistory,Project,ProjectType,Major,Bank
from django.conf import settings
from vnpay.models import Order

# Create your views here.
class ProjectManagementView(ListView):
    template_name = 'project/project-management.html'
    paginate_by = settings.PAGINATE_BY
    context_object_name = 'projects'
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class CreateProjectView(LoginRequiredMixin,TemplateView):
    login_url = 'user:login'
    template_name = 'project/create-project.html'
    model = Project
    context_object_name = 'project_details'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_types'] = ProjectType.objects.all()
        context['majors'] = Major.objects.all()
        if 'unfinished_project' in self.request.session:
            context['unfinished_project'] = Project.objects.get(pk = self.request.session['unfinished_project']['unfinished_project_pk'])
        return context

    def post(self,*args,**kwargs):
        if self.request.method == 'POST':
            if 'unfinished_project' in self.request.session:
                unfinished_project = Project.objects.get(pk=self.request.session['unfinished_project']['unfinished_project_pk'])
                unfinished_project.project_name = self.request.POST.get('project_name')
                unfinished_project.user = self.request.user
                unfinished_project.deadline = self.request.POST.get('deadline')
                unfinished_project.describe = self.request.POST.get('describe')
                unfinished_project.design_confirm = self.request.POST.get('design_confirm'),
                unfinished_project.design_file = self.request.FILES.get('file')
                unfinished_project.payment_status = Project.PaymentStatus.WAITING_FOR_DEPOSIT
                for major in self.request.POST.getlist('majors'):
                    unfinished_project.majors.add(Major.objects.get(major=major))
                
                unfinished_project.save()
                return redirect('project:rules',pk=unfinished_project.pk)
            else:
                new_project = Project.objects.create(
                    project_name = self.request.POST.get('project_name'),
                    user = self.request.user,
                    project_type = ProjectType.objects.get(type=self.request.POST.get('type')),
                    deadline = self.request.POST.get('deadline'),
                    describe = self.request.POST.get('describe'),
                    design_confirm = self.request.POST.get('design_confirm'),
                    design_file = self.request.FILES.get('file'),
                    payment_status = Project.PaymentStatus.WAITING_FOR_DEPOSIT
                )
                for major in self.request.POST.getlist('majors'):
                    new_project.majors.add(Major.objects.get(major=major))
                
                new_project.save()

                self.request.session['unfinished_project'] = {
                    'user':self.request.user.username,
                    'unfinished_project_pk': new_project.pk
                }
                return redirect('project:rules',pk=new_project.pk)

class ProjectDetailView(LoginRequiredMixin,DetailView):
    login_url = 'user:login'
    template_name = 'project/project-detail.html'

    def get(self, request, *args, **kwargs):
        try:
            project = Project.objects.get(pk=self.kwargs['pk'])
            if project.user != self.request.user:
                return redirect('ttechInfo:404')
            return render(request,self.template_name,context={
                "project":project,
                "project_types":ProjectType.objects.all(),
                "majors":Major.objects.all()
            })
        except Project.DoesNotExist:
            return redirect('ttechInfo:404')
    
    def post(self,request, *args, **kwargs):
        if self.request.method == 'POST' and 'delete-project' in self.request.POST:
            id = pk=self.kwargs['pk']
            project = Project.objects.get(pk=id)
            if project.payment_status == Project.PaymentStatus.WAITING_FOR_DEPOSIT:
                project.delete()
                return redirect("project:projects")
            else:
                return redirect("project:project-detail",pk=id)

class RulesView(LoginRequiredMixin,TemplateView):
    login_url = 'user:login'
    template_name = 'project/rules.html'

    def post(self,*args,**kwargs):
        if self.request.method == 'POST':
            new_project = Project.objects.get(pk=self.kwargs['pk'])
            new_project.rules_agree = self.request.POST.get('agree')
            new_project.save()
            if 'unfinished_project' in self.request.session:
                del self.request.session['unfinished_project']
        return redirect('project:pay',pk=self.kwargs['pk'])


def ajax_show_price(request):
    if request.method == 'POST' and request.is_ajax():
        project_type = ProjectType.objects.get(type=request.POST.get('project_type'))
        return JsonResponse(data={
            'price':project_type.price,
        },status=200)


# Thanh toán

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()

class PayView(LoginRequiredMixin,TemplateView):
    login_url = 'user:login'
    template_name='project/payment.html'

    def get(self, request, *args, **kwargs):
        context = {}
        try:
            project = Project.objects.get(pk=self.kwargs['pk'],payment_status=Project.PaymentStatus.WAITING_FOR_DEPOSIT)
            if project.user != self.request.user:
                return redirect('ttechInfo:404')
            if project.rules_agree == project.RulesAgree.NO:
                return redirect('project:rules',pk=project.pk)
            else:
                return render(request,self.template_name,context={
                    "title":"Đặt cọc dự án",
                    "project":project,
                    "banks":Bank.objects.filter(international=False),
                    "international_payments":Bank.objects.filter(international=True)
                })
        except Project.DoesNotExist:
            try:
                project = Project.objects.get(pk=self.kwargs['pk'],payment_status=Project.PaymentStatus.WAITING_FOR_PAYING)
                if project.user != self.request.user:
                    return redirect('ttechInfo:404')
                return render(request,self.template_name,context={
                    "title":"Thanh toán dự án",
                    "project":project,
                    "banks":Bank.objects.filter(international=False),
                    "international_payments":Bank.objects.filter(international=True)
                })
            except Project.DoesNotExist:
                return redirect('ttechInfo:404')

    def post(self,request, *args, **kwargs):
        if self.request.method == 'POST':
            
            project = Project.objects.get(pk=self.kwargs['pk']) # get project data

            # create order to get info that passing to api
            if project.payment_status == Project.PaymentStatus.WAITING_FOR_DEPOSIT:
                order = Order.objects.get_or_create(
                    project=project,
                    describe=f"Dat coc du an {project.pk}",
                    type=Order.OrderType.DEPOSIT
                )[0]
            elif project.payment_status == Project.PaymentStatus.WAITING_FOR_PAYING:
                order = Order.objects.get_or_create(
                    project=project,
                    describe=f"Thanh toan du an {project.pk}",
                    type=Order.OrderType.PAY
                )[0]
            order.payment_method = self.request.POST.get('payment-method')
            order.save()

            if 'bankcode' in self.request.POST:
                order.bank = Bank.objects.get(bankcode=self.request.POST.get('bankcode'))
            elif 'international-payment' in self.request.POST:
                order.bank = Bank.objects.get(bankcode=self.request.POST.get('international-payment'))
            else:
                momo = Momo(
                    request_id = "RQ2",
                    store_id = settings.STORE_ID,
                    amount = int(project.project_type.price / 2),
                    order_id = str(order.pk),
                    order_info = order.describe,
                    extra_data = "",
                    access_key = settings.ACCESS_KEY,
                    partner_code = settings.PARTNER_CODE,
                    notify_url = settings.MOMO_NOTIFY_URL,
                    return_url = settings.MOMO_RETURN_URL,
                    secret_key = settings.MOMO_SECRET_KEY,
                    momo_url = settings.API_ENDPOINT
                )
                momo.create_signature()
                return redirect(momo.get_payment_url())
                
                
            
            order.save()

            order_id = order.pk
            amount = int(project.project_type.price / 2)
            order_desc = order.describe
            bank_code = order.bank.bankcode
            language = 'vn'
            ipaddr = get_client_ip(self.request)

            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderType'] = 250000
            vnp.requestData['vnp_Locale'] = language
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_BankCode'] = bank_code
            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            return redirect(vnpay_payment_url)
        
class PaymentReturn(TemplateView):
    template_name = 'project/payment-return.html'

    def get(self, request, *args, **kwargs):
        inputData = request.GET
        if inputData:
            vnp = vnpay()
            vnp.responseData = inputData.dict()
            order_id = inputData['vnp_TxnRef']
            amount = int(inputData['vnp_Amount']) / 100
            order_desc = inputData['vnp_OrderInfo']
            vnp_TransactionNo = inputData['vnp_TransactionNo']
            vnp_ResponseCode = inputData['vnp_ResponseCode']
            vnp_TmnCode = inputData['vnp_TmnCode']
            vnp_PayDate = inputData['vnp_PayDate']
            vnp_BankCode = inputData['vnp_BankCode']
            vnp_CardType = inputData['vnp_CardType']
            if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
                if vnp_ResponseCode == "00":
                    order = Order.objects.get(pk=order_id)
                    order.status = True
                    order.save(*args,**kwargs)
                    if order.type == Order.OrderType.DEPOSIT:
                        project = order.project
                        project.payment_status = Project.PaymentStatus.DEPOSITED
                        project.save()
                    elif order.type == Order.OrderType.PAY:
                        project = order.project
                        project.payment_status = Project.PaymentStatus.FULLY_PAYED
                        project.save()
                    return render(request, self.template_name, {"title": "Kết quả thanh toán",
                                                                    "result": "Thành công", "order_id": order_id,
                                                                    "amount": amount,
                                                                    "order_desc": order_desc,
                                                                    "vnp_TransactionNo": vnp_TransactionNo,
                                                                    "vnp_ResponseCode": vnp_ResponseCode,
                                                                    "time":order.payed_time,
                                                                    'project':project})
                else:
                    order = Order.objects.get(pk=order_id)
                    project = order.project
                    return render(request, self.template_name, {"title": "Kết quả thanh toán",
                                                                    "result": "Lỗi", "order_id": order_id,
                                                                    "amount": amount,
                                                                    "order_desc": order_desc,
                                                                    "vnp_TransactionNo": vnp_TransactionNo,
                                                                    "vnp_ResponseCode": vnp_ResponseCode,
                                                                    "project":project,
                                                                    "time":timezone.now()})
            else:
                return render(request, self.template_name,
                                {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                                "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                                "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
        else:
            return render(request, self.template_name, {"title": "Kết quả thanh toán", "result": ""})

def validate_changed_data(project_name,majors):
    response = {} 
    if len(project_name) == 0 or project_name == None:
        response['project_name_response'] = "Không được để trống"
    if len(majors) == 0:
        response['majors_response'] = "Không được để trống"
    return response

def ajax_change_project(request):
    if request.method == 'POST' and request.is_ajax():
        project_name = request.POST.get("project_name")
        project_type = request.POST.get("project_type")
        majors = request.POST.getlist("majors[]")
        deadline = request.POST.get("deadline")
        description = request.POST.get("description")

        validate = validate_changed_data(project_name,majors)
        if len(validate.keys()) != 0:
            return JsonResponse(data=validate,status=400)
        else:
            project = Project.objects.get(pk=request.POST.get('project_id'))
            if project.change_detect(project_name,project_type,majors,deadline,description):
                last_update_project = ProjectChangeHistory.objects.create(
                    project=project,
                    project_name = project.project_name,
                    project_type = project.project_type,
                    deadline = project.deadline,
                    describe = project.describe,
                    design_confirm = project.design_confirm,
                    design_file = project.design_file,
                    change_order = project.change_time + 1
                )
                for major in project.majors.all():
                    last_update_project.majors.add(Major.objects.get(major=major))
                last_update_project.save()

                project.project_name = project_name
                project.project_type = ProjectType.objects.get(type=project_type)
                project.majors.clear()
                for major in majors:
                    project.majors.add(Major.objects.get(major=major))
                project.deadline = deadline
                project.describe = description
                project.change_time += 1
                # project.design_file = file
                project.save()
                return JsonResponse({
                    "message":"Update success"
                },status=200)
            else:
                return JsonResponse({
                    "message":"Nothing changed",
                },status=200)
    return JsonResponse({},status=400)



