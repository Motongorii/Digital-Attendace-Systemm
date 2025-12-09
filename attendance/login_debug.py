import logging

logger = logging.getLogger(__name__)

def lecturer_login_with_debug(request):
    """Lecturer login view with server-side debug logging."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        print(f'[LOGIN DEBUG] username={username}, auth_user={user}')
        logger.info(f'[LOGIN DEBUG] username={username}, auth_user={user}')
        
        if user is not None:
            login(request, user)
            session_key = request.session.session_key
            print(f'[LOGIN SUCCESS] username={username}, session_key={session_key}')
            logger.info(f'[LOGIN SUCCESS] username={username}, session_key={session_key}')
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            print(f'[LOGIN FAILED] username={username}, invalid credentials')
            logger.warning(f'[LOGIN FAILED] username={username}, invalid credentials')
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'attendance/login.html')
