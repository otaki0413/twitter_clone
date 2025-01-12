from django import forms

from .models import Message


class MessageCreateForm(forms.ModelForm):
    """メッセージ送信用フォーム"""

    class Meta:
        model = Message
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "placeholder": "新しいメッセージを作成",
                    "rows": 1,
                    "class": "form-control py-2",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_content(self):
        value = self.cleaned_data["content"]
        # 必要があればバリデーション追加
        return value

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
