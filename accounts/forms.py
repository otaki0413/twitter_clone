from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class SignupForm(forms.ModelForm):
    """サインアップ用のフォーム"""

    class Meta:
        model = CustomUser
        fields = [CustomUser.USERNAME_FIELD] + CustomUser.REQUIRED_FIELDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_username(self):
        value = self.cleaned_data["username"]
        # 一意性チェック
        if CustomUser.objects.filter(username=value).exists():
            raise forms.ValidationError("このユーザー名は既にに使用されています。")
        # 文字数チェック
        if len(value) < 3:
            raise forms.ValidationError(
                "%(min_length)s文字以上で入力してください", params={"min_length": 3}
            )
        return value

    def clean_email(self):
        value = self.cleaned_data["email"]
        # 一意性チェック
        if CustomUser.objects.filter(email=value).exists():
            raise forms.ValidationError("このメールアドレスは既にに使用されています。")
        return value

    def clean_tel_number(self):
        value = self.cleaned_data["tel_number"]
        return value

    def clean_birth_date(self):
        value = self.cleaned_data["birth_date"]
        return value

    def clean(self):
        # 親の clean() を明示的に呼び出して、モデルレベルのユニーク制約を自動バリデーションする
        super().clean()
