from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.contrib.auth.models import User,Group
# Create your views here.


class IndexView(TemplateView):
    template_name = 'ttechInfo/index.html'

    def get(self, request, *args, **kwargs):
        
        if self.request.user.is_authenticated:
            user = self.request.user
            if Group.objects.get(name='Admin') in user.groups.all():
                return redirect("administrator:dashboard")

        return super().get(request, *args, **kwargs)

class AboutUsView(TemplateView):
    template_name = 'ttechInfo/about.html'

class PricingView(TemplateView):
    template_name = 'ttechInfo/pricing.html'

class ServiceView(TemplateView):
    template_name = 'ttechInfo/service.html'

class ContactView(TemplateView):
    template_name = 'ttechInfo/contact.html'

class PortfolioView(TemplateView):
    template_name = 'ttechInfo/portfolio.html'

class NotFoundView(TemplateView):
    template_name = 'ttechInfo/404.html'