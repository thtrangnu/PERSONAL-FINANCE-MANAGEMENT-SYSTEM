from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import DatabaseError, connection
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
import mimetypes

from apps.accounts.forms import AvatarUploadForm, EmailOrUsernameAuthenticationForm, ProfileForm, RegisterForm
from apps.accounts.services import sync_profile_for_user


class AccountLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = EmailOrUsernameAuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = {
            'form': kwargs.get('form') or self.get_form(),
            'view': self,
            self.redirect_field_name: self.get_redirect_url(),
        }
        context.update(kwargs)
        return context


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Tạo tài khoản thành công. Chào mừng bạn đến NUFI!')
            return redirect('profile')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def google_login_start(request):
    if not settings.ALLAUTH_INSTALLED:
        messages.error(
            request,
            'Đăng nhập bằng Google hiện chưa được bật. Bạn vẫn có thể đăng nhập bằng tài khoản thường.',
        )
        return redirect('login')

    has_google_env_config = bool(settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET)
    has_google_db_config = False

    if not has_google_env_config:
        try:
            from allauth.socialaccount.models import SocialApp

            has_google_db_config = SocialApp.objects.filter(provider='google').exists()
        except DatabaseError:
            has_google_db_config = False

    if not has_google_env_config and not has_google_db_config:
        messages.error(
            request,
            'Đăng nhập bằng Google chưa sẵn sàng. Bạn vẫn có thể đăng nhập bằng tài khoản thường.',
        )
        return redirect('login')

    required_tables = {
        'django_site',
        'account_emailaddress',
        'socialaccount_socialapp',
        'socialaccount_socialaccount',
    }
    try:
        existing_tables = set(connection.introspection.table_names())
    except DatabaseError:
        existing_tables = set()

    missing_tables = required_tables - existing_tables
    if missing_tables:
        messages.error(
            request,
            'Đăng nhập bằng Google đang được chuẩn bị. Bạn vẫn có thể dùng tài khoản thường trước.',
        )
        return redirect('login')

    host = request.get_host()
    if host.startswith('localhost:'):
        port = host.split(':', 1)[1]
        return redirect(f'{request.scheme}://127.0.0.1:{port}/accounts/google/login/')

    return redirect('/accounts/google/login/')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('landing')


def _get_or_create_profile(user):
    return sync_profile_for_user(user)


@login_required
def profile(request):
    profile_obj = _get_or_create_profile(request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật hồ sơ thành công.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj, user=request.user)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile_obj})


@login_required
@require_POST
def profile_avatar_upload(request):
    profile_obj = _get_or_create_profile(request.user)
    form = AvatarUploadForm(request.POST, request.FILES)
    wants_json = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if not form.is_valid():
        error_messages = []
        for errors in form.errors.values():
            error_messages.extend(errors)
        error_message = error_messages[0] if error_messages else 'Không thể lưu ảnh đại diện.'
        if wants_json:
            return JsonResponse({'ok': False, 'error': error_message}, status=400)
        messages.error(request, error_message)
        return redirect('profile')

    profile_obj = form.save(profile_obj)
    display_name = profile_obj.full_name or profile_obj.username
    if not wants_json:
        messages.success(request, 'Đã cập nhật ảnh đại diện.')
        return redirect('profile')

    return JsonResponse(
        {
            'ok': True,
            'avatar_url': profile_obj.avatar_url,
            'display_name': display_name,
            'initial': (display_name[:1] or request.user.username[:1]).upper(),
        }
    )


@login_required
def avatar_file(request, avatar_path):
    storage_path = f'avatars/{avatar_path}'
    if not default_storage.exists(storage_path):
        raise Http404('Không tìm thấy ảnh đại diện.')

    content_type, _ = mimetypes.guess_type(storage_path)
    return FileResponse(
        default_storage.open(storage_path, 'rb'),
        content_type=content_type or 'application/octet-stream',
    )
