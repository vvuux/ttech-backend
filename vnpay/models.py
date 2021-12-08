from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from project.models import Project,ProjectType,ProjectChangeHistory,Major,Bank
# Create your models here.

class Order(models.Model):
    class PaymentMethod(models.TextChoices):
        CARD = 'Thẻ ngân hàng',_('Thẻ ngân hàng')
        E_WALLET = 'Ví điện tử',_('Ví điện tử')
        INTERNATIONAL_CARD = 'Thẻ thanh toán quốc tế',_('Thẻ thanh toán quốc tế')
    
    class OrderType(models.TextChoices):
        DEPOSIT = 'Đặt cọc',_('Đặt cọc')
        PAY = 'Thanh toán',_('Thanh toán')
    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name='orders')
    payment_method = models.CharField(max_length=50,choices=PaymentMethod.choices,null=True,blank=True)
    describe = models.TextField(max_length=100)
    type = models.CharField(max_length=20,choices=OrderType.choices)
    status = models.BooleanField(default=False)
    bank = models.ForeignKey(Bank,on_delete=models.CASCADE,related_name='orders',null=True,blank=True)
    payed_time = models.DateTimeField(null=True,blank=True)

    def save(self,*args,**kwargs):
        if not self.payed_time and self.status==True:
            self.payed_time = timezone.now()
        return super().save(*args,**kwargs)