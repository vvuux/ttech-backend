from django.urls import path,include
from ttechInfo import views

app_name = 'ttechInfo'

urlpatterns = [
    path('home/',views.IndexView.as_view(),name='home'),
    path('about/',views.AboutUsView.as_view(),name='about'),
    path('portfolio/',views.PortfolioView.as_view(),name='portfolio'),
    path('pricing/',views.PricingView.as_view(),name='pricing'),
    path('service/',views.ServiceView.as_view(),name='services'),
    path('contact/',views.ContactView.as_view(),name='contact'),
    path('notfound404/',views.NotFoundView.as_view(),name='404')
]