from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to set additional data on user object.
        """
        user = super().save_user(request, user, form, commit=False)
        # カスタムユーザーの追加フィールド設定
        user.tel_number = form.cleaned_data.get("tel_number")
        user.birth_date = form.cleaned_data.get("birth_date")
        user.save()
