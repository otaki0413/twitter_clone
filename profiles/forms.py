from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model


class ProfileEditForm(forms.ModelForm):
    """プロフィール編集用フォーム"""

    class Meta:
        model = get_user_model()
        fields = [
            "name",
            "description",
            "location",
            "website",
            "birth_date",
            "icon_image",
            "header_image",
        ]
        # 各フィールドのウィジェット設定
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "icon_image": forms.FileInput(),
            "header_image": forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 各フィールドにBootstrap適用
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_name(self):
        value = self.cleaned_data["name"]
        # 必要があればバリデーション追加
        return value

    def clean_description(self):
        value = self.cleaned_data["description"]
        # 必要があればバリデーション追加
        return value

    def clean_location(self):
        value = self.cleaned_data["location"]
        # 必要があればバリデーション追加
        return value

    def clean_birth_date(self):
        value = self.cleaned_data["birth_date"]
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
