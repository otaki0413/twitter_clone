from datetime import datetime
import re

from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class SignupForm(forms.ModelForm):
    """サインアップ用のフォーム"""

    class Meta:
        model = CustomUser
        fields = [CustomUser.USERNAME_FIELD] + CustomUser.REQUIRED_FIELDS

    # MEMO: clean_birth_date()内だと、日付フォーマットのバリデーションがかけられなかったので、フィールドレベルで指定している
    birth_date = forms.DateField(
        input_formats=["%Y-%m-%d"],  # YYYY-MM-DD形式
        error_messages={"invalid": "YYYY-MM-DD形式で入力してください。"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_username(self):
        value = self.cleaned_data["username"]
        errors = []
        # 一意性チェック
        if CustomUser.objects.filter(username=value).exists():
            errors.append("このユーザー名は既に使用されています。")
        # 文字数チェック
        if len(value) < 3:
            errors.append(
                "%(min_length)s文字以上で入力してください。" % {"min_length": 3}
            )
        if errors:
            raise forms.ValidationError(errors)
        return value

    def clean_email(self):
        value = self.cleaned_data["email"]
        # 一意性チェック
        if CustomUser.objects.filter(email=value).exists():
            raise forms.ValidationError("このメールアドレスは既に使用されています。")
        return value

    def clean_tel_number(self):
        value = self.cleaned_data["tel_number"]
        errors = []
        # 正規表現チェック
        if not re.match(r"^\d+$", value):
            errors.append("数字のみで入力してください。")
        # 文字数チェック
        if len(value) < 10 or len(value) > 15:
            errors.append("10文字以上15文字以内で入力してください。")
        if errors:
            raise forms.ValidationError(errors)
        return value

    def clean_birth_date(self):
        value = self.cleaned_data["birth_date"]
        errors = []
        # 未来の日付チェック
        today = datetime.today().date()
        if value > today:
            errors.append("未来の日付はいけません。正しい日付を入力してください。")
        if errors:
            raise forms.ValidationError(errors)
        return value

    def clean(self):
        # 親の clean() を明示的に呼び出して、モデルレベルのユニーク制約を自動バリデーションする
        super().clean()
