from django import forms

from .models import Tweet, Comment


class TweetCreateForm(forms.ModelForm):
    """ツイート投稿用フォーム"""

    class Meta:
        model = Tweet
        fields = ["content", "image"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "placeholder": "いまどうしてる？",
                    "rows": 3,
                    "class": "form-control",
                }
            ),
            "image": forms.FileInput(attrs={"class": "d-none"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_content(self):
        value = self.cleaned_data["content"]
        # 必要があればバリデーション追加
        return value

    def clean_image(self):
        value = self.cleaned_data["image"]
        # 必要があればバリデーション追加
        return value

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class CommentCreateForm(forms.ModelForm):
    """コメント投稿用フォーム"""

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "placeholder": "返信をツイート",
                    "rows": 2,
                    "class": "form-control",
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
