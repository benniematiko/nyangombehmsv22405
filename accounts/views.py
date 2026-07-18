from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        # FIXED: Changed from 'dashboard' to 'dashboard:home'
        return redirect('dashboard:home') 
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # FIXED: Changed from 'dashboard' to 'dashboard:home'
                return redirect('dashboard:home') 
        messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})
def logout_view(request):
    """
    Step 1: Renders the 'Are you sure?' confirmation page.
    Protects the view by shifting unauthenticated users directly to login.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return render(request, 'accounts/logout_confirm.html')


def logout_execute_view(request):
    """
    Step 2: Receives the secure POST request from the confirmation page form delay.
    Destroys the session data and drops a success toast message into the system.
    """
    if request.method == 'POST':
        logout(request)
        # Injects the success message that your login page JavaScript/HTML reads
        messages.success(request, 'You have been successfully logged out.')
        return redirect('accounts:login')
        
    # If a user attempts to manually force-type this URL into the bar, bounce them home safely
    return redirect('dashboard:home')