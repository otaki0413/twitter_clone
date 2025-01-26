from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator

from .models import Tweet, Comment, Like, Retweet, Bookmark
from notifications.models import Notification
from .forms import TweetCreateForm, CommentCreateForm


class TimelineView(
    LoginRequiredMixin,
    ListView,
):
    """おすすめのツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/index.html"
    login_url = reverse_lazy("accounts:login")
    paginate_by = 5

    def get_queryset(self):
        return Tweet.get_timeline_tweets(requesting_user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["form"] = TweetCreateForm
        return context


class FollowingTweetListView(
    LoginRequiredMixin,
    ListView,
):
    """フォロー中のツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/following.html"
    login_url = reverse_lazy("accounts:login")
    paginate_by = 5

    def get_queryset(self):
        return Tweet.get_following_tweets(requesting_user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["form"] = TweetCreateForm
        return context


class BookmarkListView(LoginRequiredMixin, ListView):
    """ブックマークしたツイート一覧ビュー"""

    model = Tweet
    template_name = "tweets/bookmark.html"
    login_url = reverse_lazy("accounts:login")
    paginate_by = 5

    def get_queryset(self):
        return Tweet.get_bookmarked_tweets(requesting_user=self.request.user)


class TweetCreateView(CreateView):
    """ツイート投稿用のビュー"""

    model = Tweet
    form_class = TweetCreateForm

    def get(self, request, *args, **kwargs):
        # GETリクエスト時には直前のページへリダイレクト
        return redirect(request.META.get("HTTP_REFERER", "tweets:timeline"))

    def get_success_url(self):
        # リファラーURLに応じて、リダイレクト先を切り替える
        if "/following" in self.request.META.get("HTTP_REFERER", ""):
            return reverse_lazy("tweets:following")
        else:
            return reverse_lazy("tweets:timeline")

    def form_valid(self, form):
        # フォームからインスタンス取得（※まだ保存しない）
        tweet = form.save(commit=False)
        # ユーザーの設定
        tweet.user = self.request.user
        tweet.save()
        messages.success(
            self.request,
            "ツイートの投稿に成功しました。",
            extra_tags="success",
        )
        # 親クラスの保存処理を実行
        return super().form_valid(form)

    def form_invalid(self, form):
        # リファラーURLに応じた設定
        if "/following" in self.request.META.get("HTTP_REFERER", ""):
            queryset = Tweet.get_following_tweets(requesting_user=self.request.user)
            template_name = "tweets/following.html"
        else:
            queryset = Tweet.get_timeline_tweets(requesting_user=self.request.user)
            template_name = "tweets/index.html"

        # ページネーター作成
        paginator = Paginator(queryset, 5)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # バリデーションエラー時の再描画用のコンテキスト生成
        context = {
            "form": form,
            "tweet_list": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "is_paginated": True,
        }

        # ページ再描画
        return render(self.request, template_name, context)


class TweetDetailView(LoginRequiredMixin, DetailView):
    """ツイート詳細ビュー"""

    model = Tweet
    template_name = "tweets/detail.html"

    def get_queryset(self):
        return Tweet.get_tweet_detail().filter(pk=self.kwargs["pk"])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tweet = self.object
        relations = self.request.user.get_relations()
        # ツイートにログインユーザー情報を付与
        tweet.add_status(requesting_user=self.request.user, relations=relations)
        context["tweet"] = tweet
        context["form"] = CommentCreateForm()
        return context


class CommentCreateView(CreateView):
    """コメント投稿ビュー"""

    model = Comment
    form_class = CommentCreateForm
    template_name = "tweets/detail.html"

    def get(self, request, *args, **kwargs):
        # GETリクエスト時には詳細へリダイレクトさせる
        # MEMO:コメント投稿のフォームエラー時にURLが`/tweets/{int:pk}/comment`となるのに対処するために、リダイレクト先を明示的に指定
        return redirect("tweets:tweet_detail", pk=self.kwargs["pk"])

    def get_success_url(self):
        # ツイート詳細ページへリダイレクト
        return reverse_lazy("tweets:tweet_detail", kwargs={"pk": self.kwargs["pk"]})

    def form_valid(self, form):
        try:
            # トランザクション開始
            with transaction.atomic():
                # フォームからインスタンス取得（※まだ保存しない）
                comment = form.save(commit=False)
                # ユーザーの設定
                comment.user = self.request.user
                # ツイートの設定
                comment.tweet = Tweet.objects.get(pk=self.kwargs["pk"])
                # コメント保存
                comment.save()
                # 自身以外に対して通知作成
                send_email = False
                if not comment.user == comment.tweet.user:
                    send_email = True
                    Notification.create_notification(
                        notification_type_name="comment",
                        sender=comment.user,
                        receiver=comment.tweet.user,
                        tweet=comment.tweet,
                    )
                messages.success(
                    self.request,
                    "コメントの投稿に成功しました。",
                    extra_tags="success",
                )
        except Tweet.DoesNotExist:
            messages.error(
                self.request, "ツイートが存在しませんでした。", extra_tags="danger"
            )
        except IntegrityError:
            messages.error(
                self.request,
                "いいねの処理中にエラーが発生しました。",
                extra_tags="danger",
            )
        except Exception as e:
            messages.error(
                self.request,
                f"予期しないエラーが発生しました: {str(e)}",
                extra_tags="danger",
            )
        else:
            # 通知フラグがONの場合、メール通知
            if send_email:
                send_mail(
                    subject="コメントされました！🎉",
                    message=f"{self.request.user.username}さんがあなたのツイートにコメントしました。",
                    from_email=settings.FROM_EMAIL,
                    recipient_list=[comment.tweet.user.email],
                )

        finally:
            return super().form_valid(form)

    def form_invalid(self, form):
        tweet = Tweet.get_tweet_detail().get(pk=self.kwargs["pk"])
        relations = self.request.user.get_relations()
        tweet.add_status(requesting_user=self.request.user, relations=relations)
        # バリデーションエラー時の再描画用のコンテキスト生成
        context = {
            "tweet": tweet,
            "form": form,
        }
        # ツイート詳細ページ再描画
        return render(self.request, "tweets/detail.html", context)


class LikeToggleView(LoginRequiredMixin, View):
    """いいね・いいね解除を切り替えるビュー"""

    def post(self, request, *args, **kwargs):
        try:
            # リクエストをもとにツイート情報を取得
            tweet = Tweet.objects.get(pk=request.POST.get("tweet_id"))
            # ログインユーザを取得
            user = request.user

            # 対象のいいね情報を取得
            try:
                target_like = Like.objects.get(user=user, tweet=tweet)
            except Like.DoesNotExist:
                target_like = None

            with transaction.atomic():
                # いいねの切り替え処理
                if target_like is None:
                    # いいね追加
                    tweet.likes.create(user=user)
                    # 自身以外に対して通知作成
                    send_email = False
                    if not user == tweet.user:
                        send_email = True
                        Notification.create_notification(
                            notification_type_name="like",
                            sender=user,
                            receiver=tweet.user,
                            tweet=tweet,
                        )
                    messages.success(
                        self.request,
                        "いいねをしました。",
                        extra_tags="success",
                    )
                else:
                    # いいね削除
                    target_like.delete()
                    messages.success(
                        self.request,
                        "いいねを解除しました。",
                        extra_tags="success",
                    )
        except Tweet.DoesNotExist:
            messages.error(
                self.request, "ツイートが存在しませんでした。", extra_tags="danger"
            )
        except IntegrityError:
            messages.error(
                self.request,
                "いいねの処理中にエラーが発生しました。",
                extra_tags="danger",
            )
        except Exception as e:
            messages.error(
                self.request,
                f"予期しないエラーが発生しました: {str(e)}",
                extra_tags="danger",
            )
        else:
            # 通知フラグがONの場合、メール通知
            if send_email:
                send_mail(
                    subject="いいねされました！🎉",
                    message=f"{user.username}さんがあなたのツイートをいいねしました。",
                    from_email=settings.FROM_EMAIL,
                    recipient_list=[tweet.user.email],
                )
        finally:
            # 直前のページにリダイレクトする
            return redirect(request.META.get("HTTP_REFERER", "tweets:timeline"))


class RetweetToggleView(LoginRequiredMixin, View):
    """リツイート・リツイート解除を切り替えるビュー"""

    def post(self, request, *args, **kwargs):
        try:
            # リクエストをもとにツイート情報を取得
            tweet = Tweet.objects.get(pk=request.POST.get("tweet_id"))
            # ログインユーザを取得
            user = request.user

            # 対象のリツイート情報を取得
            try:
                target_retweet = tweet.retweets.get(user=user)
            except Retweet.DoesNotExist:
                target_retweet = None

            # トランザクション開始
            with transaction.atomic():
                # リツイートの切り替え処理
                if target_retweet is None:
                    # リツイート
                    tweet.retweets.create(user=user)
                    # 自身以外に対して通知作成
                    send_email = False
                    if not user == tweet.user:
                        send_email = True
                        Notification.create_notification(
                            notification_type_name="retweet",
                            sender=user,
                            receiver=tweet.user,
                            tweet=tweet,
                        )
                    messages.success(
                        self.request,
                        "リツイートしました。",
                        extra_tags="success",
                    )
                else:
                    # リツイート解除
                    target_retweet.delete()
                    messages.success(
                        self.request,
                        "リツイートを解除しました。",
                        extra_tags="success",
                    )
        except Tweet.DoesNotExist:
            messages.error(
                self.request, "ツイートが存在しませんでした。", extra_tags="danger"
            )
        except IntegrityError:
            messages.error(
                self.request,
                "リツイートの処理中にエラーが発生しました。",
                extra_tags="danger",
            )
        except Exception as e:
            messages.error(
                self.request,
                f"予期しないエラーが発生しました: {str(e)}",
                extra_tags="danger",
            )
        else:
            # 通知フラグがONの場合、メール通知
            if send_email:
                send_mail(
                    subject="リツイートされました！🎉",
                    message=f"{user.username}さんがあなたのツイートをリツイートしました。",
                    from_email=settings.FROM_EMAIL,
                    recipient_list=[tweet.user.email],
                )
        finally:
            # 直前のページにリダイレクトする
            return redirect(request.META.get("HTTP_REFERER", "tweets:timeline"))


class BookmarkToggleView(LoginRequiredMixin, View):
    """ブックマーク・ブックマーク解除を切り替えるビュー"""

    def post(self, request, *args, **kwargs):
        # リクエストをもとにツイート情報を取得
        tweet = Tweet.objects.get(pk=request.POST.get("tweet_id"))
        # ログインユーザを取得
        user = request.user

        # 対象のブックマーク情報を取得
        try:
            target_bookmark = tweet.bookmarks.get(user=user)
        except Bookmark.DoesNotExist:
            target_bookmark = None

        # ブックマークの切り替え処理
        if target_bookmark is None:
            # ブックマーク
            tweet.bookmarks.create(user=user)
            messages.success(
                self.request,
                "ブックマークしました。",
                extra_tags="success",
            )
        else:
            # ブックマーク解除
            target_bookmark.delete()
            messages.success(
                self.request,
                "ブックマークを解除しました。",
                extra_tags="success",
            )

        # 直前のページにリダイレクトする
        return redirect(request.META.get("HTTP_REFERER", "tweets:timeline"))
