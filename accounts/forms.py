from datetime import datetime
import re

from django import forms
from django.contrib.auth import get_user_model

from allauth.account.forms import SignupForm, LoginForm


# カスタムユーザー取得
CustomUser = get_user_model()


class CustomSignupForm(SignupForm):
    """カスタムサインアップフォーム"""

    # 追加対象のフィールド
    tel_number = forms.CharField(max_length=15, required=False)
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )

    def __init__(self, *args, **kwargs):
        # 親クラスのinit呼び出す
        super().__init__(*args, **kwargs)

        # 各フィールドにBootstrap適用
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        # プレースホルダーを空にする
        self.fields["username"].widget.attrs["placeholder"] = ""
        self.fields["email"].widget.attrs["placeholder"] = ""
        self.fields["password1"].widget.attrs["placeholder"] = ""

    def clean_username(self):
        value = self.cleaned_data["username"]
        # 一意性チェック
        if CustomUser.objects.filter(username=value).exists():
            raise forms.ValidationError("このユーザー名は既に使用されています。")
        # 文字数チェック
        if len(value) < 3:
            raise forms.ValidationError("3文字以上で入力してください。")
        return value

    def clean_email(self):
        value = self.cleaned_data["email"]
        # 一意性チェック
        if CustomUser.objects.filter(email=value).exists():
            raise forms.ValidationError("このメールアドレスは既に使用されています。")
        return value

    def clean_password1(self):
        value = self.cleaned_data["password1"]
        # 必要があればバリデーション追加
        return value

    def clean_tel_number(self):
        value = self.cleaned_data["tel_number"]
        if value:
            # 正規表現チェック
            if not re.match(r"^\d+$", value):
                raise forms.ValidationError("数字のみで入力してください。")
            # 文字数チェック
            if len(value) < 10 or len(value) > 15:
                raise forms.ValidationErrorationError(
                    "10文字以上15文字以内で入力してください。"
                )
        return value

    def clean_birth_date(self):
        value = self.cleaned_data["birth_date"]  # <class 'datetime.date'>
        if value:
            # 未来の日付チェック
            if value > datetime.today().date():
                raise forms.ValidationError(
                    "未来の日付はいけません。正しい日付を入力してください。"
                )
            return value

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, request):
        # SignupFormのsaveメソッド呼び出す、内部的にadapterのsave_userが実行されている
        user = super().save(request)
        # user.tel_number = self.cleaned_data.get("tel_number")
        # user.birth_date = self.cleaned_data.get("birth_date")
        # user.save()
        return user


class CustomLoginForm(LoginForm):
    """カスタムログインフォーム"""

    def __init__(self, *args, **kwargs):
        # 親クラスのinit呼び出す
        super().__init__(*args, **kwargs)

        # 各フィールドにBootstrap適用
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        # プレースホルダーを空にする
        self.fields["login"].widget.attrs["placeholder"] = ""
        self.fields["password"].widget.attrs["placeholder"] = ""

    def clean_login(self):
        value = self.cleaned_data["login"]
        # DB存在チェック
        if not CustomUser.objects.filter(email=value).exists():
            raise forms.ValidationError("未登録のメールアドレスです。")
        return value

    def clean_password(self):
        value = self.cleaned_data["password"]
        return value

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def login(self, *args, **kwargs):
        return super().login(*args, **kwargs)
