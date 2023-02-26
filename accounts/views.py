from django.shortcuts import render, redirect
from django_nextjs.render import render_nextjs_page_sync
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import json
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout

# From this app
from .forms import NewUserForm

# SignUp page's view
@unauthenticated_user
@csrf_exempt
def signUpView(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            messages.success(request, 'Account successfully created.')

            messages_data = []
            for message in messages.get_messages(request):
                message_data = {
                    'level': message.level,
                    'message': message.message,
                    'extra_tags': message.tags
                }
                messages_data.append(message_data)

            response_data = {
                'success': True,
                'messages': messages_data
            }

            return HttpResponse(json.dumps(response_data), content_type='application/json')

        else:
            for error in form.errors.values():
                messages.error(request, error)
                
            messages_data = []
            for message in messages.get_messages(request):
                message_data = {
                    'level': message.level,
                    'message': message.message[0],
                    'extra_tags': message.tags
                }
                messages_data.append(message_data)

            response_data = {
                'success': False,
                'messages': messages_data
            }
                

            return HttpResponse(json.dumps(response_data), content_type='application/json')

    return render_nextjs_page_sync(request)

# SignIn page's view
@unauthenticated_user
@csrf_exempt
def signInView(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if request.user.is_staff:
                isStaff = True
            else:
                isStaff = False

            response_data = {
                'success': True,
                'isStaff': isStaff
            }

            return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            messages.error(request, 'Wrong username or password')

            for error in form.errors.values():
                messages.error(request, error)
                
            messages_data = []
            for message in messages.get_messages(request):
                message_data = {
                    'level': message.level,
                    'message': message.message,
                    'extra_tags': message.tags
                }
                messages_data.append(message_data)

            response_data = {
                'success': False,
                'messages': messages_data
            }
                
            return HttpResponse(json.dumps(response_data), content_type='application/json')

    return render_nextjs_page_sync(request)

@csrf_exempt
def logoutUser(request):
    logout(request)
    return HttpResponse()
