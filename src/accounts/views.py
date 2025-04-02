from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth

def decide_next_url(next_url):
    if next_url is None or len(next_url) == 0 or next_url == reverse('accounts:login_view'):
        next_url = reverse('writing:index')
    return next_url

# Create your views here.
def login_view(request):
    if request.user is not None and request.user.is_active:
        return HttpResponseRedirect(reverse('writing:index'))
    if request.method == 'POST':  # 本地用户登录
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        next_url = decide_next_url(request.POST.get('next', ''))
        if user is not None and user.is_active:
            # Correct password, and the user is marked 'active'
            auth.login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            # Show an error page
            return render(request, 'accounts/login.html', {'next': next_url})
    else:  # GET method
        code = request.GET.get('code', '')
        next_url = decide_next_url(request.GET.get('next', ''))
        return render(
            request,
            'accounts/login.html',
            {
                'next': next_url,
            }
        )


def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('accounts:login_view'))