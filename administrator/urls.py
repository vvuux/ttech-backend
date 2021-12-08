from django.urls import path,include

from administrator import views
app_name = 'administrator'

urlpatterns = [
    path("dashboard/",views.DashboardView.as_view(),name='dashboard'),
    path("dashboard/projects/",views.ProjectDashboardView.as_view(),name='projects-dashboard'),
    path("dashboard/profile/<int:pk>/",views.UserProfileDashboardView.as_view(),name='user-profile'),
    path("dashboard/profile/all-user/",views.AllUserView.as_view(),name='all-user'),
    path("ajax-permission-update/",views.ajax_permission_update,name="ajax-permission-update"),
    path("dashboard/project/<int:pk>/",views.ProjectDetailDashboardView.as_view(),name='project-detail-dashboard'),
    path("dashboard/ajax-add-task/",views.ajax_add_task,name="ajax-add-task"),
    path("dashboard/ajax-check-task/?done=<str:done>",views.ajax_check_task,name="ajax-check-task"),
    path("dashboard/ajax-delete-task/",views.ajax_delete_task,name="ajax-delete-task"),
    path("dashboard/email/compose/",views.EmailComposeView.as_view(),name="email-compose"),
    
]