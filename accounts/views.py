from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

from .forms import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm
from .models import Role
from .otp_utils import generate_otp, verify_otp, generate_password_reset_otp, verify_password_reset_otp

User = get_user_model()


def _get_school_context():
    """Return common context used by all auth pages."""
    from core.models import School

    school = School.objects.first()
    return {
        "school_name": school.name if school else "Preskool",
        "school_logo": school.logo.url if school and school.logo else None,
    }


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            remember_me = form.cleaned_data.get("remember_me", False)

            user = authenticate(request, username=username_or_email, password=password)

            if user is None:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(
                        request, username=user_obj.username, password=password
                    )
                except User.DoesNotExist:
                    user = None

            if user is not None:
                if not user.is_active:
                    messages.error(
                        request, "Your account is inactive. Please contact the administrator."
                    )
                    return render(
                        request, "accounts/login.html", {"form": form, **_get_school_context()}
                    )

                if not user.is_email_verified:
                    request.session["otp_user_id"] = user.pk
                    messages.warning(
                        request, "Please verify your email address. We've sent a new OTP to your email."
                    )
                    generate_otp(user)
                    return redirect("accounts:verify-otp")

                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                next_url = request.GET.get("next", "home")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form, **_get_school_context()})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            generate_otp(user)
            request.session["otp_user_id"] = user.pk
            messages.success(
                request,
                "Account created! Please verify your email with the OTP we sent.",
            )
            return redirect("accounts:verify-otp")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    context = {"form": form, "roles": Role.objects.all(), **_get_school_context()}
    return render(request, "accounts/register.html", context)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("accounts:login")


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=user_email, is_active=True)
                # Generate and send password reset OTP
                generate_password_reset_otp(user)
                request.session["reset_password_otp_user_id"] = user.pk
                messages.success(
                    request,
                    "A password reset OTP has been sent to your email address. "
                    "Please check your inbox.",
                )
                return redirect("accounts:forgot-password-verify-otp")
            except User.DoesNotExist:
                messages.error(request, "No active account found with this email.")
    else:
        form = ForgotPasswordForm()

    return render(
        request, "accounts/forgot-password.html", {"form": form, **_get_school_context()}
    )


def password_reset_done_view(request):
    return render(
        request, "accounts/password-reset-done.html", _get_school_context()
    )


def reset_password_view(request, uidb64=None, token=None):
    if request.user.is_authenticated:
        return redirect("home")

    if uidb64 is not None and token is not None:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            messages.error(request, "This password reset link is invalid or has expired.")
            return redirect("accounts:forgot-password")
    else:
        # Check session indicating successful password reset OTP verification
        user_id = request.session.get("reset_password_verified_user_id")
        if not user_id:
            messages.error(request, "Session expired or invalid request. Please request OTP again.")
            return redirect("accounts:forgot-password")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("accounts:forgot-password")

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password"])
            user.save()
            if "reset_password_verified_user_id" in request.session:
                del request.session["reset_password_verified_user_id"]
            messages.success(
                request,
                "Your password has been reset successfully. You can now log in.",
            )
            return redirect("accounts:login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ResetPasswordForm()

    context = {
        "form": form,
        "validlink": True,
        "uidb64": uidb64,
        "token": token,
        **_get_school_context(),
    }
    return render(request, "accounts/reset-password.html", context)


def verify_otp_view(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please register or log in again.")
        return redirect("accounts:login")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please register again.")
        return redirect("accounts:register")

    if user.is_email_verified:
        login(request, user)
        messages.success(request, f"Welcome, {user.get_full_name() or user.username}!")
        return redirect("home")

    if request.method == "POST":
        otp_code = request.POST.get("otp_code", "").strip()
        if not otp_code:
            messages.error(request, "Please enter the OTP code.")
            return render(request, "accounts/verify_otp.html", {
                "email": user.email,
                **_get_school_context(),
            })

        success, msg = verify_otp(user, otp_code)
        if success:
            messages.success(request, msg)
            del request.session["otp_user_id"]
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, msg)

    return render(request, "accounts/verify_otp.html", {
        "email": user.email,
        **_get_school_context(),
    })


def resend_otp_view(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please register or log in again.")
        return redirect("accounts:login")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please register again.")
        return redirect("accounts:register")

    if user.is_email_verified:
        login(request, user)
        return redirect("home")

    generate_otp(user)
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("accounts:verify-otp")


def forgot_password_verify_otp_view(request):
    user_id = request.session.get("reset_password_otp_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please request OTP again.")
        return redirect("accounts:forgot-password")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("accounts:forgot-password")

    if request.method == "POST":
        otp_code = request.POST.get("otp_code", "").strip()
        if not otp_code:
            messages.error(request, "Please enter the OTP code.")
            return render(request, "accounts/forgot_password_verify_otp.html", {
                "email": user.email,
                **_get_school_context(),
            })

        success, msg = verify_password_reset_otp(user, otp_code)
        if success:
            messages.success(request, "OTP verified successfully. You can now reset your password.")
            del request.session["reset_password_otp_user_id"]
            request.session["reset_password_verified_user_id"] = user.pk
            return redirect("accounts:reset-password-direct")
        else:
            messages.error(request, msg)

    return render(request, "accounts/forgot_password_verify_otp.html", {
        "email": user.email,
        **_get_school_context(),
    })


def forgot_password_resend_otp_view(request):
    user_id = request.session.get("reset_password_otp_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please request OTP again.")
        return redirect("accounts:forgot-password")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("accounts:forgot-password")

    generate_password_reset_otp(user)
    messages.success(request, "A new password reset OTP has been sent to your email.")
    return redirect("accounts:forgot-password-verify-otp")
