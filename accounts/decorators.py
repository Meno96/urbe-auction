from django.shortcuts import redirect

# If the user is authenticated it will be redirected to the home otherwise continues the function
def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('auction:homepage')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func