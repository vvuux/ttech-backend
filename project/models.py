from datetime import time
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime
# Create your models here.

class BaseInfo(models.Model):
    created_date = models.DateTimeField(editable=False)

    class Meta:
        abstract = True

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'files/customer-design/user_{0}/{1}'.format(instance.user.pk, filename)

def bank_directory_path(instance, filename):
    return 'images/logo/bank/{0}/{1}'.format(instance.bankcode, filename)

def project_user_directory_path(instance,filename):
    return 'files/projects/user_{0}/{1}'.format(instance.user.pk,filename)

class Project(BaseInfo):
    class DesignConfirm(models.TextChoices):
        YES = 'Có',_('Có')
        NO = 'Không',_('Không')
    class PaymentStatus(models.TextChoices):
        DEPOSITED = 'Đã đặt cọc',_('Đã đặt cọc')
        WAITING_FOR_DEPOSIT = 'Chờ đặt cọc',_('Chờ đặt cọc')
        FULLY_PAYED = 'Đã thanh toán',_('Đã thanh toán')
        WAITING_FOR_PAYING = 'Chờ thanh toán',_('Chờ thanh toán')
    class RulesAgree(models.TextChoices):
        YES = 'Đồng ý',_('Đã đồng ý điều khoản')
        NO = 'Chưa đồng ý',_("Chưa đồng ý điều khoản")
    project_name = models.CharField(max_length=256)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='projects')
    project_type = models.ForeignKey("ProjectType",on_delete=models.CASCADE,related_name='projects')
    majors = models.ManyToManyField("Major")
    deadline = models.DateTimeField()
    describe = models.TextField(max_length=10000,null=True,blank=True)
    progress = models.IntegerField(default=0,editable=False)
    design_confirm = models.CharField(max_length=10,choices=DesignConfirm.choices,default=DesignConfirm.NO)
    design_file = models.FileField(upload_to=user_directory_path,null=True,blank=True)
    payment_status = models.CharField(max_length=50,choices=PaymentStatus.choices,default=PaymentStatus.WAITING_FOR_DEPOSIT)
    change_time = models.IntegerField(default=0,editable=False)
    final_project_file = models.FileField(upload_to=project_user_directory_path,null=True,blank=True)
   
    rules_agree = models.CharField(max_length=30,choices=RulesAgree.choices,default=RulesAgree.NO)

    def change_detect(self,project_name,project_type,majors,deadline,description):
        majors_check = False
        if len(majors) >= len(self.majors.all()):
            majors_check = any([Major.objects.get(major=major) not in self.majors.all() for major in majors])
        elif len(self.majors) > len(majors):
            majors_check = any([major.major not in majors for major in self.majors.all()])
        return any([
                self.project_name != project_name,
                self.project_type != ProjectType.objects.get(type=project_type),
                majors_check,
                datetime.datetime.isoformat(self.deadline) != deadline,
                self.describe != description,
            ])

    def __str__(self):
        return str(self.project_name) + "-" + str(self.user)

    def save(self, *args, **kwargs):
        if self.final_project_file and self.payment_status ==self.PaymentStatus.DEPOSITED:
            self.payment_status = self.PaymentStatus.WAITING_FOR_PAYING
        if not self.created_date:
            self.created_date = timezone.now()
        if self.design_file:
            self.design_confirm = self.DesignConfirm.YES
        else:
            self.design_confirm = self.DesignConfirm.NO
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date','deadline','-progress']

    def deposit_price(self):
        return self.project_type.price / 2 
    



class Major(models.Model):
    major = models.CharField(max_length=50)

    def __str__(self):
        return str(self.major)

class ProjectType(models.Model):
    type = models.CharField(max_length=100)
    price = models.FloatField()

    def __str__(self):
        return str(self.type)

class ProjectChangeHistory(models.Model):
    class DesignConfirm(models.TextChoices):
        YES = 'Có',_('Có')
        NO = 'Không',_('Không')
    class PaymentStatus(models.TextChoices):
        DEPOSITED = 'Đã đặt cọc',_('Đã đặt cọc')
        WAITING_FOR_DEPOSIT = 'Chờ đặt cọc',_('Chờ đặt cọc')
        FULLY_PAYED = 'Đã thanh toán',_('Đã thanh toán')
        WAITING_FOR_PAYING = 'Chờ thanh toán',_('Chờ thanh toán')
    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name='change_histories')
    project_name = models.CharField(max_length=256)
    project_type = models.ForeignKey("ProjectType",on_delete=models.CASCADE)
    majors = models.ManyToManyField("Major")
    deadline = models.DateTimeField()
    describe = models.TextField(max_length=10000)
    design_confirm = models.CharField(max_length=10,choices=DesignConfirm.choices,default=DesignConfirm.NO)
    design_file = models.FileField(upload_to=user_directory_path)
    change_date = models.DateField(editable=False)
    change_order = models.IntegerField(editable=False,default=0)

    def save(self, *args, **kwargs):
        if not self.change_date:
            self.change_date = timezone.now()
        return super().save( *args, **kwargs)

    class Meta:
        ordering = ['project','-change_date','-change_order']

    def __str__(self):
        return str(self.project.pk) + " - " + str(self.change_date) + " - " + str(self.change_order)



class Bank(models.Model):
    bankcode = models.CharField(max_length=50,unique=True,primary_key=True)
    bank = models.CharField(max_length=300,unique=True)
    logo = models.ImageField(upload_to=bank_directory_path)
    international = models.BooleanField(default=False)

    def __str__(self):
        return str(self.bankcode)

class ProgressDetail(models.Model):
    class TaskStatus(models.TextChoices):
        FINISHED = "Hoàn thành",_("Hoàn thành")
        NOT_FINISHED = "Chưa hoàn thành",_("Chưa hoàn thành")
    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name="tasks")
    task = models.CharField(max_length=300)
    status = models.CharField(max_length=30,choices=TaskStatus.choices,default=TaskStatus.NOT_FINISHED)
    done_time = models.DateTimeField(null=True,blank=True,editable=False)

    def save(self, *args, **kwargs):
        if self.status == self.TaskStatus.FINISHED and not self.done_time:
            self.done_time = timezone.now()
        if self.status == self.TaskStatus.NOT_FINISHED and self.done_time:
            self.done_time = None
        super().save( *args, **kwargs)
        self.project.progress = self.calc_progress_percent()
        self.project.save()

    def calc_progress_percent(self):
        done_task_num = ProgressDetail.objects.filter(project=self.project,status=self.TaskStatus.FINISHED).count()
        all_task_num = ProgressDetail.objects.filter(project=self.project).count()
        if all_task_num == 0:
            return 0
        progress = int(done_task_num*100/all_task_num)
        return progress

    @staticmethod
    def static_calc_progress_percent(project,status):
        done_task_num = ProgressDetail.objects.filter(project=project,status=status).count()
        all_task_num = ProgressDetail.objects.filter(project=project).count()
        if all_task_num == 0:
            return 0
        progress = int(done_task_num*100/all_task_num)
        return progress

    def delete(self, *args, **kwargs):
        project_id = self.project.pk
        super().delete(args,kwargs)
        project = Project.objects.get(pk=project_id)
        project.progress = ProgressDetail.static_calc_progress_percent(project,ProgressDetail.TaskStatus.FINISHED)
        project.save()

