from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.contrib.auth.models import User,Group
from django.conf import settings

from user.models import UserProfile
from project.models import ProgressDetail
# Create your views here.

from project.models import Project

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'administrator/dashboard.html'
    login_url = 'user:login'


class ProjectDashboardView(TemplateView):
    template_name = 'administrator/project-dashboard.html'
    
    def get(self, request, *args, **kwargs):
        kwargs['projects'] = Project.objects.all()
        kwargs['deposited_projects'] = Project.objects.filter(payment_status=Project.PaymentStatus.DEPOSITED)
        kwargs['finished_projects'] = Project.objects.filter(payment_status=Project.PaymentStatus.WAITING_FOR_PAYING)
        kwargs['payed_projects'] = Project.objects.filter(payment_status=Project.PaymentStatus.FULLY_PAYED)
        return super().get(request, *args, **kwargs)

    
class UserProfileDashboardView(TemplateView):
    template_name = 'administrator/user-profile.html'

    def get(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        kwargs['user'] = User.objects.get(pk=user_id)
        kwargs['groups'] = Group.objects.all()
        return super().get(request, *args, **kwargs)

class AllUserView(TemplateView):
    template_name = 'administrator/all-user.html'

    def get(self, request, *args, **kwargs):
        kwargs['users'] = UserProfile.objects.all()
        admin = Group.objects.get(name='Admin')
        kwargs['admin_users'] = User.objects.filter(groups__name='Admin')

        return super().get(request, *args, **kwargs)


def ajax_permission_update(request):
    if request.method == "POST" and request.is_ajax():
        pk = request.POST.get('user')
        user = User.objects.get(pk=pk)
        groups = request.POST.getlist('permission[]')
        if len(groups) == 0:
            return JsonResponse({
                "message":"Không được để trống",
            },status=400)
        else:
            user.groups.clear()
            for group in groups:
                user.groups.add(Group.objects.get(name=group))
        user.save()
        return JsonResponse(data={
            "message":"Thành công"
        },status=200)
    return JsonResponse({},status=400)


class ProjectDetailDashboardView(TemplateView):
    template_name = 'administrator/project-details-dashboard.html'

    def get(self, request, *args, **kwargs):
        kwargs['project'] = Project.objects.get(pk=self.kwargs['pk'])
        kwargs['tasks'] = ProgressDetail.objects.filter(project=Project.objects.get(pk=self.kwargs['pk']))
        return super().get(request, *args, **kwargs)

    def post(self,request, *args, **kwargs):
        if self.request.method == 'POST' and 'project-file-upload' in self.request.POST:
            project = Project.objects.get(pk=self.kwargs['pk'])
            project.final_project_file = self.request.FILES.get('project-file')
            project.save()
            return redirect("administrator:project-detail-dashboard",pk=kwargs['pk'])


def ajax_add_task(request):
    if request.method == "POST" and request.is_ajax():
        print("OK")
        project = Project.objects.get(pk=request.POST.get('project_id'))
        if request.POST.get('task') == "":
            return JsonResponse(data={
                "message":"Không được để trống"
            },status=400)
        else:
            new_task = ProgressDetail.objects.create(
                project=project,
                task=request.POST.get('task')
            )
            return JsonResponse(data={
                "message":"Thành công",
                "task_id":new_task.pk,
                "new_task":new_task.task,
                "progress":project.progress
            },status=200)


def ajax_check_task(request, *args, **kwargs):
    if request.method == "POST" and request.is_ajax():
        done = kwargs['done']
        task_id = request.POST.get('task_id')
        if done == "true":
            task = ProgressDetail.objects.get(pk=task_id)
            task.status = ProgressDetail.TaskStatus.FINISHED
            task.save()
        else:
            task = ProgressDetail.objects.get(pk=task_id)
            task.status = ProgressDetail.TaskStatus.NOT_FINISHED
            task.save()
        return JsonResponse(data={
            "message":"Hoàn thành",
            "progress": task.project.progress
        },status=200)
    return JsonResponse(data={},status=400)


def ajax_delete_task(request):
    if request.method == "POST" and request.is_ajax():
        task_id = request.POST.get('task_id')
        task = ProgressDetail.objects.get(pk=task_id)
        project_id = task.project.pk
        task.delete()
        return JsonResponse(data={
            "message":"Thành công",
            "progress": Project.objects.get(pk=project_id).progress
        },status=200)
    return JsonResponse(data={},status=400)

def get_email_address_list(lst:str):
    if lst == [""]:
        return lst
    email_lst = []
    email_lst.extend([email_address.strip() for email_address in lst[0].split(",")])
    return email_lst

def validate_files(files:list):
    size = 0
    size_limit = settings.FILE_SIZE_LIMIT
    for file in files:
        print(file,file.size)
        size += file.size
    if size > size_limit:
        return False
    return True
    
class EmailComposeView(TemplateView):
    template_name = "administrator/email-compose.html"

    def post(self,*args,**kwargs):
        if self.request.method == "POST":
            to = get_email_address_list(self.request.POST.getlist('to'))
            bcc = get_email_address_list(self.request.POST.getlist('bcc'))
            cc = get_email_address_list(self.request.POST.getlist('cc'))
            subject = self.request.POST.get('subject')
            body_text = self.request.POST.get('body_text')
            attachments = self.request.FILES.getlist('attachments')

            email_messsage = EmailMessage(
                subject=subject,
                body=body_text,
                from_email=settings.EMAIL_HOST_USER,
                to = to,
                bcc=bcc,
                cc=cc,
            )

            if self.request.FILES:
                if validate_files(attachments) == False:
                    return render(self.request,self.template_name,context={
                        "error":"File gửi đi không được quá 5MB",
                        "form_data":{
                            "to":self.request.POST.get('to'),
                            "bcc":self.request.POST.get("bcc"),
                            "cc": self.request.POST.get("cc"),
                            "subject": self.request.POST.get("subject"),
                            "body_text": self.request.POST.get("body_text")
                        }
                    })
                for file in attachments:
                    email_messsage.attach(file.name,file.read(),file.content_type)
            email_messsage.send()
            return render(self.request,self.template_name,context={
                "message":"Gửi thành công"
            })