from django.urls import path,include

from project import views

app_name = 'project'

urlpatterns = [
    path('projects/',views.ProjectManagementView.as_view(),name='projects'),
    path('project/<int:pk>/',views.ProjectDetailView.as_view(),name='project-detail'),
    path('project/create/',views.CreateProjectView.as_view(),name='create-project'),
    path('ajax-price/',views.ajax_show_price,name='ajax-show-price'),
    path('project/<int:pk>/rules/',views.RulesView.as_view(),name='rules'),
    path('project/<int:pk>/pay/',views.PayView.as_view(),name='pay'),
    path('project/payment-return/',views.PaymentReturn.as_view(),name='payment-return'),
    path('ajax-change-project/',views.ajax_change_project,name='ajax-change-project'),
]