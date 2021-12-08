from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from project.models import Project
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    personal_picture = models.ImageField(upload_to='images/personal_picture')
    birthday = models.DateField(null=True,blank=True)
    phone = models.CharField(max_length=10,null=True,blank=True)
    
    def __str__(self):
        return str(self.user.username) + "\'s Profile"

    def number_of_project(self):
        return Project.objects.filter(user=self.user).count()

    def number_of_deposited_project(self):
        return Project.objects.filter(user=self.user,payment_status=Project.PaymentStatus.DEPOSITED).count()

    def number_of_finished_project(self):
        return Project.objects.filter(user=self.user,payment_status=Project.PaymentStatus.FULLY_PAYED).count()

