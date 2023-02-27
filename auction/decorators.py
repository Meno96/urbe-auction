from django.shortcuts import redirect

# If the user is authenticated it will be redirected to the home otherwise continues the function
def only_staff(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('auction:homepage')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func
