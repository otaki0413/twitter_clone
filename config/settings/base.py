from pathlib import Path

# --------------------
# Build paths
# --------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# --------------------
# Core settings
# --------------------
INSTALLED_APPS = [
    "accounts.apps.AccountsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --------------------
# Authentication
# --------------------
# カスタムユーザーモデルの設定
AUTH_USER_MODEL = "accounts.CustomUser"
# サインアップ・ログインフォームの設定
ACCOUNT_FORMS = {
    "signup": "accounts.forms.CustomSignupForm",
    "login": "accounts.forms.CustomLoginForm",
}
# サインアップ時のアダプターの設定
ACCOUNT_ADAPTER = "accounts.adapter.AccountAdapter"
# サインアップ・ログイン後のリダイレクト先URL
LOGIN_REDIRECT_URL = "accounts:home"
# ユーザー認証にメールアドレスを使用
ACCOUNT_AUTHENTICATION_METHOD = "email"
# ユーザー登録にユーザー名を必須にする
ACCOUNT_USERNAME_REQUIRED = True
# ユーザー登録にメールアドレスを必須にする
ACCOUNT_EMAIL_REQUIRED = True
# パスワードの入力を1回にする
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
# 認証済みユーザーのリダイレクトを防止させる
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
# メールの確認を無効化
ACCOUNT_EMAIL_VERIFICATION = "none"
# ユーザー登録後、メールアドレスに確認メールが送信される
ACCOUNT_EMAIL_VERIFICATION = "none"
# 認証情報をセッションに保存しない
ACCOUNT_SESSION_REMEMBER = True


# --------------------
# Internationalization
# --------------------
LANGUAGE_CODE = "ja"

TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_TZ = True


# --------------------
# Static files
# --------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"


# --------------------
# Password validation
# --------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# --------------------
# Default primary key settings
# --------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
