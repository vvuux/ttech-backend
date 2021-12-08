from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LogoutView, logout_then_login

from user.models import UserProfile
from project.models import Project
# Create your views here.

class Loginview(TemplateView):
    template_name = 'user/login-signup.html'

    def post(self,*args,**kwargs):
        """
        authenticate then check user group is admin or not
        if user is admin, redirect to admin page
        else if user is client, redirect to client page 
        """
        if self.request.method == 'POST' and 'login' in self.request.POST:
            username = self.request.POST.get('lg-username')
            password = self.request.POST.get('lg-password')
            
            user = authenticate(username=username,password=password)

            if user is not None:
                login(self.request,user)

                admin_check = User.objects.get(username=username).groups.all().filter(name='Admin').exists()

                if admin_check == True:
                    return redirect('administrator:dashboard')
                else:
                    if self.request.GET.get("next"):
                        return redirect(self.request.GET.get("next"))
                    return redirect('ttechInfo:home')

        elif self.request.method == 'POST' and 'signup' in self.request.POST:
            if self.request.POST.get('signup-password') != self.request.POST.get('signup-password-again'):
                return redirect('/')
            else:
                try:
                    User.objects.get(username=self.request.POST.get('signup-username'))
                    return redirect('user:login')
                except User.DoesNotExist:        
                    username = self.request.POST.get('signup-username')
                    email = self.request.POST.get('signup-email')
                    first_name = self.request.POST.get('signup-firstname')
                    last_name = self.request.POST.get('signup-lastname')
                    phone = self.request.POST.get('signup-phone')
                    password = self.request.POST.get('signup-password')
                    
                    # create new client user
                    user = User(username=username,email=email,first_name=first_name,last_name=last_name)
                    user.set_password(password)
                    user.save(*args,**kwargs)
                    
                    # add group Client
                    client_group = Group.objects.get(name='Client')
                    user.groups.add(client_group)
                    
                    # create new user profile
                    user_profile = UserProfile.objects.create(user=user,phone=phone)
                    return redirect('user:login')
        
        return redirect('/')

@login_required(login_url='/login/')
def user_logout(request):
    if 'unfinished_project' in request.session:
        unfinished_project = Project.objects.get(pk=request.session['unfinished_project']['unfinished_project_pk'])
        unfinished_project.delete()
    logout(request)
    return redirect('ttechInfo:home')