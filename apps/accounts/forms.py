from pathlib import Path
import unicodedata
from uuid import uuid4

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from django.utils.text import get_valid_filename

from apps.accounts.models import UserProfile
from apps.accounts.services import sync_profile_for_user


TIMEZONE_CHOICES = [
    {
        'value': 'Asia/Ho_Chi_Minh',
        'label': 'Hà Nội / TP. Hồ Chí Minh, Việt Nam (UTC+7)',
        'aliases': [
            'ha noi',
            'hanoi',
            'ho chi minh',
            'hcm',
            'sai gon',
            'saigon',
            'viet nam',
            'vietnam',
        ],
    },
    {
        'value': 'Asia/Bangkok',
        'label': 'Bangkok, Thái Lan (UTC+7)',
        'aliases': ['bangkok', 'thai lan', 'thailand'],
    },
    {
        'value': 'Asia/Jakarta',
        'label': 'Jakarta, Indonesia (UTC+7)',
        'aliases': ['jakarta', 'indonesia'],
    },
    {
        'value': 'Asia/Singapore',
        'label': 'Singapore (UTC+8)',
        'aliases': ['singapore', 'sing'],
    },
    {
        'value': 'Asia/Kuala_Lumpur',
        'label': 'Kuala Lumpur, Malaysia (UTC+8)',
        'aliases': ['kuala lumpur', 'malaysia'],
    },
    {
        'value': 'Asia/Manila',
        'label': 'Manila, Philippines (UTC+8)',
        'aliases': ['manila', 'philippines', 'philippin'],
    },
    {
        'value': 'Asia/Hong_Kong',
        'label': 'Hong Kong (UTC+8)',
        'aliases': ['hong kong', 'hk'],
    },
    {
        'value': 'Asia/Shanghai',
        'label': 'Shanghai / Bắc Kinh, Trung Quốc (UTC+8)',
        'aliases': ['shanghai', 'beijing', 'bac kinh', 'trung quoc', 'china'],
    },
    {
        'value': 'Asia/Taipei',
        'label': 'Taipei, Đài Loan (UTC+8)',
        'aliases': ['taipei', 'dai loan', 'taiwan'],
    },
    {
        'value': 'Asia/Tokyo',
        'label': 'Tokyo, Nhật Bản (UTC+9)',
        'aliases': ['tokyo', 'nhat ban', 'japan'],
    },
    {
        'value': 'Asia/Seoul',
        'label': 'Seoul, Hàn Quốc (UTC+9)',
        'aliases': ['seoul', 'han quoc', 'korea'],
    },
    {
        'value': 'Asia/Dubai',
        'label': 'Dubai, UAE (UTC+4)',
        'aliases': ['dubai', 'uae', 'united arab emirates'],
    },
    {
        'value': 'Asia/Kolkata',
        'label': 'Mumbai / New Delhi, Ấn Độ (UTC+5:30)',
        'aliases': ['mumbai', 'new delhi', 'india', 'an do'],
    },
    {
        'value': 'Europe/London',
        'label': 'London, Vương quốc Anh (UTC+0/+1)',
        'aliases': ['london', 'uk', 'england'],
    },
    {
        'value': 'Europe/Paris',
        'label': 'Paris, Pháp (UTC+1/+2)',
        'aliases': ['paris', 'phap', 'france'],
    },
    {
        'value': 'Europe/Berlin',
        'label': 'Berlin, Đức (UTC+1/+2)',
        'aliases': ['berlin', 'duc', 'germany'],
    },
    {
        'value': 'Europe/Rome',
        'label': 'Rome, Ý (UTC+1/+2)',
        'aliases': ['rome', 'roma', 'y', 'italy'],
    },
    {
        'value': 'Europe/Madrid',
        'label': 'Madrid, Tây Ban Nha (UTC+1/+2)',
        'aliases': ['madrid', 'tay ban nha', 'spain'],
    },
    {
        'value': 'Europe/Amsterdam',
        'label': 'Amsterdam, Hà Lan (UTC+1/+2)',
        'aliases': ['amsterdam', 'ha lan', 'netherlands'],
    },
    {
        'value': 'Europe/Moscow',
        'label': 'Moscow, Nga (UTC+3)',
        'aliases': ['moscow', 'nga', 'russia'],
    },
    {
        'value': 'America/New_York',
        'label': 'New York, Hoa Kỳ (UTC-5/-4)',
        'aliases': ['new york', 'nyc', 'hoa ky', 'usa'],
    },
    {
        'value': 'America/Chicago',
        'label': 'Chicago, Hoa Kỳ (UTC-6/-5)',
        'aliases': ['chicago', 'illinois', 'usa central'],
    },
    {
        'value': 'America/Denver',
        'label': 'Denver, Hoa Kỳ (UTC-7/-6)',
        'aliases': ['denver', 'colorado', 'usa mountain'],
    },
    {
        'value': 'America/Los_Angeles',
        'label': 'Los Angeles, Hoa Kỳ (UTC-8/-7)',
        'aliases': ['los angeles', 'la', 'california', 'usa pacific'],
    },
    {
        'value': 'America/Toronto',
        'label': 'Toronto, Canada (UTC-5/-4)',
        'aliases': ['toronto', 'canada'],
    },
    {
        'value': 'America/Vancouver',
        'label': 'Vancouver, Canada (UTC-8/-7)',
        'aliases': ['vancouver', 'canada pacific'],
    },
    {
        'value': 'America/Sao_Paulo',
        'label': 'São Paulo, Brazil (UTC-3)',
        'aliases': ['sao paulo', 'brazil', 'brasil'],
    },
    {
        'value': 'Australia/Sydney',
        'label': 'Sydney, Úc (UTC+10/+11)',
        'aliases': ['sydney', 'uc', 'australia'],
    },
    {
        'value': 'Australia/Melbourne',
        'label': 'Melbourne, Úc (UTC+10/+11)',
        'aliases': ['melbourne', 'uc', 'australia'],
    },
    {
        'value': 'Pacific/Auckland',
        'label': 'Auckland, New Zealand (UTC+12/+13)',
        'aliases': ['auckland', 'new zealand', 'nz'],
    },
    {
        'value': 'Africa/Cairo',
        'label': 'Cairo, Ai Cập (UTC+2/+3)',
        'aliases': ['cairo', 'ai cap', 'egypt'],
    },
    {
        'value': 'Africa/Johannesburg',
        'label': 'Johannesburg, Nam Phi (UTC+2)',
        'aliases': ['johannesburg', 'nam phi', 'south africa'],
    },
    {
        'value': 'UTC',
        'label': 'UTC - Giờ phối hợp quốc tế',
        'aliases': ['utc', 'gmt'],
    },
]

TIMEZONE_LABEL_BY_VALUE = {
    option['value']: option['label']
    for option in TIMEZONE_CHOICES
}


def _normalize_lookup(value):
    value = unicodedata.normalize('NFD', value or '')
    value = ''.join(char for char in value if unicodedata.category(char) != 'Mn')
    return ' '.join(value.lower().replace('_', ' ').replace('/', ' ').split())


def _build_timezone_lookup():
    lookup = {}
    for option in TIMEZONE_CHOICES:
        lookup[_normalize_lookup(option['value'])] = option['value']
        lookup[_normalize_lookup(option['label'])] = option['value']
        for alias in option['aliases']:
            lookup[_normalize_lookup(alias)] = option['value']
    return lookup


TIMEZONE_LOOKUP = _build_timezone_lookup()
TIMEZONE_SUGGESTIONS = [
    {
        'label': option['label'],
        'value': option['value'],
        'search': ' | '.join([option['label'], option['value'], *option['aliases']]),
    }
    for option in TIMEZONE_CHOICES
]


def _save_profile_avatar(profile, avatar):
    old_url = profile.avatar_url or ''
    old_path = ''
    if old_url.startswith(settings.MEDIA_URL):
        old_path = old_url.removeprefix(settings.MEDIA_URL).lstrip('/')

    suffix = Path(avatar.name).suffix.lower()
    safe_stem = get_valid_filename(Path(avatar.name).stem) or 'avatar'
    filename = f'{safe_stem}-{uuid4().hex[:12]}{suffix}'
    saved_path = default_storage.save(f'avatars/{filename}', avatar)

    if old_path and old_path != saved_path and default_storage.exists(old_path):
        default_storage.delete(old_path)

    return default_storage.url(saved_path)

try:
    from allauth.socialaccount.forms import SignupForm as SocialSignupForm
except ImportError:
    SocialSignupForm = None


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Tên đăng nhập hoặc email')

    def clean(self):
        login_value = self.cleaned_data.get('username')
        if login_value and '@' in login_value:
            user = User.objects.filter(email__iexact=login_value).first()
            if user is None:
                profile = UserProfile.objects.filter(email__iexact=login_value).first()
                if profile is not None:
                    user = User.objects.filter(username=profile.username).first()
            if user is not None:
                self.cleaned_data['username'] = user.username
        return super().clean()


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=120)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['username'].help_text = (
            'Có thể dùng chữ cái, số và các ký tự @ . + - _.'
        )
        self.fields['username'].widget.attrs.pop('placeholder', None)
        self.fields['email'].label = 'Email'
        self.fields['full_name'].label = 'Họ và tên'
        self.fields['phone_number'].label = 'Số điện thoại'
        self.fields['password1'].label = 'Mật khẩu'
        self.fields['password2'].label = 'Nhập lại mật khẩu'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists() or UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if UserProfile.objects.filter(username=username).exists():
            raise forms.ValidationError('Tên đăng nhập này đã được sử dụng.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        full_name = self.cleaned_data['full_name'].strip()
        name_parts = full_name.split(maxsplit=1)
        user.first_name = name_parts[0] if name_parts else ''
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''

        if commit:
            user.save()
            UserProfile.objects.create(
                username=user.username,
                email=user.email,
                password_hash=user.password,
                full_name=full_name,
                phone_number=self.cleaned_data.get('phone_number') or None,
                role=UserProfile.ROLE_ADMIN if user.is_staff else UserProfile.ROLE_USER,
                is_active=user.is_active,
            )
        return user


if SocialSignupForm is not None:
    class GoogleSignupForm(SocialSignupForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'username' in self.fields:
                self.fields['username'].label = 'Tên đăng nhập'
                self.fields['username'].help_text = (
                    'Có thể dùng chữ cái, số và các ký tự @ . + - _.'
                )
                self.fields['username'].widget.attrs.pop('placeholder', None)
                self.fields['username'].initial = ''
                self.initial['username'] = ''
            if 'email' in self.fields:
                self.fields['email'].label = 'Email'
                self.fields['email'].help_text = 'Email này được lấy từ tài khoản Google của bạn.'

        def clean_username(self):
            username = super().clean_username().strip()
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError('Tên đăng nhập này đã được sử dụng.')
            if UserProfile.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError('Tên đăng nhập này đã được sử dụng.')
            return username

        def save(self, request):
            user = super().save(request)
            username = self.cleaned_data.get('username', '').strip()
            if username and user.username != username:
                user.username = username
                user.save(update_fields=['username'])
            sync_profile_for_user(user)
            return user
else:
    class GoogleSignupForm(forms.Form):
        pass


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    timezone_search = forms.CharField(
        label='Múi giờ',
        required=False,
        help_text='Gõ tên thành phố, ví dụ: Ha Noi, Ho Chi Minh, Bangkok, Tokyo.',
    )
    class Meta:
        model = UserProfile
        fields = ('full_name', 'phone_number', 'timezone')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['first_name'].label = 'Tên'
        self.fields['last_name'].label = 'Họ'
        self.fields['email'].label = 'Email'
        self.fields['full_name'].label = 'Họ và tên hiển thị'
        self.fields['phone_number'].label = 'Số điện thoại'
        self.fields['timezone'].required = False
        self.fields['timezone'].widget = forms.HiddenInput(attrs={
            'data-timezone-value': 'true',
        })
        current_timezone = self.initial.get('timezone') or getattr(self.instance, 'timezone', '') or ''
        self.fields['timezone_search'].initial = TIMEZONE_LABEL_BY_VALUE.get(
            current_timezone,
            current_timezone,
        )
        self.fields['timezone_search'].widget.attrs.update({
            'autocomplete': 'off',
            'data-timezone-search': 'true',
            'placeholder': 'Gõ Ha Noi, Tokyo, New York...',
        })
        self.timezone_suggestions = TIMEZONE_SUGGESTIONS
        if user is not None:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.user and User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        if self.instance and UserProfile.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        timezone_search = cleaned_data.get('timezone_search', '')
        timezone_value = cleaned_data.get('timezone', '')

        selected_timezone = TIMEZONE_LOOKUP.get(_normalize_lookup(timezone_search))
        if timezone_search and selected_timezone is None:
            self.add_error(
                'timezone_search',
                'Vui lòng chọn múi giờ trong danh sách gợi ý.',
            )
            return cleaned_data

        if selected_timezone is None:
            selected_timezone = TIMEZONE_LOOKUP.get(_normalize_lookup(timezone_value))

        cleaned_data['timezone'] = selected_timezone or ''
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user is not None:
            first_name = self.cleaned_data.get('first_name', '').strip()
            last_name = self.cleaned_data.get('last_name', '').strip()
            combined_name = ' '.join(part for part in [first_name, last_name] if part).strip()

            self.user.first_name = first_name
            self.user.last_name = last_name
            self.user.email = self.cleaned_data['email']
            profile.email = self.cleaned_data['email']
            profile.username = self.user.username
            profile.password_hash = self.user.password
            profile.is_active = self.user.is_active
            profile.role = UserProfile.ROLE_ADMIN if self.user.is_staff else UserProfile.ROLE_USER
            if combined_name and 'full_name' not in self.changed_data:
                profile.full_name = combined_name
        profile.default_currency = profile.default_currency or 'VND'
        if commit:
            if self.user is not None:
                self.user.save()
            profile.save()
        return profile


class AvatarUploadForm(forms.Form):
    avatar = forms.FileField(
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']

        if avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Ảnh đại diện không được lớn hơn 2MB.')

        content_type = getattr(avatar, 'content_type', '')
        if content_type and not content_type.startswith('image/'):
            raise forms.ValidationError('Vui lòng chọn đúng file hình ảnh.')

        return avatar

    def save(self, profile):
        profile.avatar_url = _save_profile_avatar(profile, self.cleaned_data['avatar'])
        profile.save(update_fields=['avatar_url', 'updated_at'])
        return profile
