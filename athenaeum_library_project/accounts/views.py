from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.http import require_POST
from .forms import MemberRegisterForm, MemberLoginForm, MemberProfileForm
from circulation.models import BorrowSlip
from library.models import ReadingList, BookBag

def register_view(request):
    if request.user.is_authenticated:
        return redirect('library:home')
    if request.method == 'POST':
        form = MemberRegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            parts = cd['full_name'].strip().split(' ', 1)
            user = User.objects.create_user(username=cd['username'], email=cd['email'], password=cd['password'], first_name=parts[0], last_name=parts[1] if len(parts)>1 else '')
            if cd.get('account_role') == 'librarian':
                user.is_staff = True
                user.is_superuser = True
                user.save()
            prof = user.member_profile
            prof.full_name = cd['full_name']
            prof.phone_number = cd['phone_number']
            prof.department_or_grade = cd['department_or_grade']
            prof.save()
            login(request, user)
            messages.success(request, f'Welcome to The Athenaeum, {cd["full_name"]} ({prof.member_code}).')
            return redirect('library:librarian_console' if user.is_staff else 'library:home')
    else:
        form = MemberRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('library:home')
    if request.method == 'POST':
        form = MemberLoginForm(request.POST)
        if form.is_valid():
            ident = form.cleaned_data['identifier'].strip()
            pw = form.cleaned_data['password']
            uname = ident
            if '@' in ident:
                m = User.objects.filter(email__iexact=ident).first()
                if m: uname = m.username
            user = authenticate(request, username=uname, password=pw)
            if user:
                login(request, user)
                request.session.set_expiry(1209600 if form.cleaned_data.get('remember_me') else 0)
                messages.success(request, f'Welcome back, {user.member_profile.full_name or user.username}.')
                return redirect(request.GET.get('next') or ('library:librarian_console' if user.is_staff else 'library:home'))
            messages.error(request, 'Invalid credentials.')
    else:
        form = MemberLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'Signed out of library portal.')
    return redirect('library:home')

@login_required
def member_dashboard(request):
    tab = request.GET.get('tab', 'overview')
    slips = BorrowSlip.objects.filter(user=request.user).prefetch_related('items')
    rlist, _ = ReadingList.objects.get_or_create(user=request.user)
    bag, _ = BookBag.objects.get_or_create(user=request.user)
    profile_form = MemberProfileForm(instance=request.user.member_profile, user=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        act = request.POST.get('action')
        if act == 'update_profile':
            profile_form = MemberProfileForm(request.POST, request.FILES, instance=request.user.member_profile, user=request.user)
            if profile_form.is_valid():
                profile_form.save()
                request.user.email = profile_form.cleaned_data['email']
                request.user.save()
                messages.success(request, 'Member card & profile updated.')
                return redirect('/accounts/dashboard/?tab=settings')
        elif act == 'change_password':
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                u = password_form.save()
                update_session_auth_hash(request, u)
                messages.success(request, 'Password updated.')
                return redirect('/accounts/dashboard/?tab=password')

    return render(request, 'accounts/dashboard.html', {
        'tab': tab,
        'slips': slips,
        'saved_items': rlist.items.select_related('book'),
        'bag': bag,
        'profile_form': profile_form,
        'password_form': password_form,
    })
