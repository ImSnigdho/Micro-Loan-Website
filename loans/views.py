from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

from .models import SiteSettings, UserProfile, LoanApplication, Transaction, InboxMessage
from .forms import (
    RegisterForm, LoginForm, LoanApplicationForm, NIDUploadForm,
    WithdrawForm, PasswordChangeForm
)


def get_settings():
    return SiteSettings.get()


# ─── AUTH ────────────────────────────────────────────────────────────────────

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
        )
        UserProfile.objects.create(
            user=user,
            phone=data['phone'],
            occupation=data['occupation'],
        )
        auth_login(request, user)
        messages.success(request, 'নিবন্ধন সফল হয়েছে!')
        return redirect('home')
    return render(request, 'loans/register.html', {'form': form, 'settings': get_settings()})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        user = authenticate(request, username=data['username'], password=data['password'])
        if user:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'ইউজার নেম বা পাসওয়ার্ড ভুল।')
    return render(request, 'loans/login.html', {'form': form, 'settings': get_settings()})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


# ─── HOME ─────────────────────────────────────────────────────────────────────

@login_required
def home_view(request):
    site = get_settings()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    unread_count = InboxMessage.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'loans/index.html', {
        'settings': site,
        'profile': profile,
        'unread_count': unread_count,
    })


# ─── LOAN APPLICATION ────────────────────────────────────────────────────────

@login_required
def loan_apply_view(request):
    site = get_settings()
    form = LoanApplicationForm(request.POST or None)
    nid_form = NIDUploadForm()

    if request.method == 'POST':
        if 'apply_loan' in request.POST and form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.interest_rate = site.interest_rate_min
            deposit_pct = site.security_deposit_percent / Decimal('100')
            loan.security_deposit = Decimal(str(loan.amount)) * deposit_pct
            loan.save()
            return redirect('loan_detail', pk=loan.pk)

    return render(request, 'loans/loan_apply.html', {
        'form': form,
        'nid_form': nid_form,
        'settings': site,
    })


@login_required
def loan_detail_view(request, pk):
    site = get_settings()
    loan = get_object_or_404(LoanApplication, pk=pk, user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Handle NID upload on this page to cleanly report errors
    if request.method == 'POST' and 'submit_nid' in request.POST:
        nid_form = NIDUploadForm(request.POST, request.FILES, instance=loan)
        if nid_form.is_valid():
            nid_form.save()
            messages.success(request, 'ডকুমেন্ট সফলভাবে জমা দেওয়া হয়েছে!')
            return redirect('home')
        else:
            for field in nid_form:
                for error in field.errors:
                    messages.error(request, error)
            for error in nid_form.non_field_errors():
                messages.error(request, error)
    else:
        nid_form = NIDUploadForm(instance=loan)

    # Build repayment schedule
    import calendar
    from datetime import date
    schedule = []
    base_date = loan.applied_at.date() if hasattr(loan.applied_at, 'date') else date.today()
    for i in range(1, loan.duration_months + 1):
        month = (base_date.month - 1 + i) % 12 + 1
        year = base_date.year + ((base_date.month - 1 + i) // 12)
        day = min(base_date.day, calendar.monthrange(year, month)[1])
        due_date = date(year, month, day)
        principal = round(loan.amount / loan.duration_months, 2)
        interest = round(Decimal(str(loan.amount)) * loan.interest_rate / Decimal('100'), 2)
        total = round(Decimal(str(principal)) + interest, 2)
        schedule.append({
            'date': due_date.strftime('%b %d, %Y'),
            'principal': f'৳{principal:,.2f}',
            'interest': f'৳{interest:,.2f}',
            'total': f'৳{total:,.2f}',
        })

    return render(request, 'loans/loan_detail.html', {
        'loan': loan,
        'schedule': schedule,
        'nid_form': nid_form,
        'settings': site,
        'profile': profile,
    })


@login_required
def my_loans_view(request):
    site = get_settings()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    loans = LoanApplication.objects.filter(user=request.user)
    return render(request, 'loans/my_loans.html', {
        'loans': loans,
        'settings': site,
        'profile': profile,
    })


# ─── PROFILE ──────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    site = get_settings()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = PasswordChangeForm(request.POST or None)

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            messages.success(request, 'প্রোফাইল ছবি পরিবর্তন হয়েছে।')
            return redirect('profile')
            
        elif form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            messages.success(request, 'পাসওয়ার্ড পরিবর্তন হয়েছে। আবার লগইন করুন।')
            return redirect('login')

    return render(request, 'loans/profile.html', {
        'form': form,
        'profile': profile,
        'settings': site,
    })


# ─── WITHDRAW ─────────────────────────────────────────────────────────────────

@login_required
def withdraw_view(request):
    site = get_settings()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = WithdrawForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        amount = data['amount']

        if amount > profile.balance:
            messages.error(request, 'পর্যাপ্ত ব্যালেন্স নেই।')
        else:
            Transaction.objects.create(
                user=request.user,
                transaction_type='withdrawal',
                amount=amount,
                payment_method=data['payment_method'],
                phone_number=data['phone_number'],
                status='pending',
            )
            profile.balance -= amount
            profile.save()
            messages.success(request, 'উইথড্রো অনুরোধ জমা হয়েছে।')
            return redirect('home')

    return render(request, 'loans/withdraw.html', {
        'form': form,
        'profile': profile,
        'settings': site,
    })


# ─── INBOX ────────────────────────────────────────────────────────────────────

@login_required
def inbox_view(request):
    site = get_settings()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    msgs = InboxMessage.objects.filter(user=request.user)
    msgs.filter(is_read=False).update(is_read=True)
    return render(request, 'loans/inbox.html', {
        'messages_list': msgs,
        'settings': site,
        'profile': profile,
    })


# ─── TRANSACTIONS ─────────────────────────────────────────────────────────────

@login_required
def transactions_view(request):
    site = get_settings()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    txns = Transaction.objects.filter(user=request.user)
    return render(request, 'loans/transactions.html', {
        'transactions': txns,
        'settings': site,
        'profile': profile,
    })
