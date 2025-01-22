# テーブル設計
```mermaid
---
title: "TwitterクローンER図"
---
erDiagram
    User ||--o{ Tweet : "posts"
    User ||--o{ FollowRelation : "follows"
    User ||--o{ FollowRelation : "followed by"
    User ||--o{ Like : "makes"
    User ||--o{ Retweet : "makes"
    User ||--o{ Bookmark : "makes"
    User ||--o{ Comment : "makes"
    User ||--o{ Message : "sends"
    User ||--o{ Message : "receives"
    User ||--o{ Notification : "sends"
    User ||--o{ Notification : "receives"
    Tweet ||--o{ Like  : "has"
    Tweet ||--o{ Retweet  : "has"
    Tweet ||--o{ Bookmark  : "has"
    Tweet ||--o{ Comment  : "has"
    Tweet ||--o{ Notification : "has"
    NotificationType ||--|{ Notification : ""


    User {
        bigint id PK "ID"
        varchar name "氏名"
        varchar username "ユーザー名"
        varchar description "説明"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    FollowRelation {
        bigint id PK "ID"
        bigint follower_id FK "フォローする人のID"
        bigint followee_id FK "フォローされる人のID"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    Tweet {
        bigint id PK "ID"
        bigint user_id FK "ユーザーID"
        varchar content "ツイート内容"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    Like {
        bigint id PK "ID"
        bigint tweet_id FK "ツイートID"
        bigint user_id FK "ユーザーID"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    Retweet {
        bigint id PK "ID"
        bigint tweet_id FK "ツイートID"
        bigint user_id FK "ユーザーID"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    Comment {
        bigint id PK "ID"
        bigint tweet_id FK "ツイートID"
        bigint user_id FK "コメントした人のID"
        varchar content "コメント内容"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    Bookmark {
        bigint id PK "ID"
        bigint tweet_id FK "ツイートID"
        bigint user_id FK "ユーザーID"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    Message {
        bigint id PK "ID"
        bigint sender_id FK "送信者ID"
        bigint receiver_id FK "受信者ID"
        varchar content "メッセージ内容"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    Notification {
        bigint id PK "ID"
        bigint type_id FK "通知タイプID"
        bigint sender_id FK "通知者ID"
        bigint receiver_id FK "受信者ID"
        bigint tweet_id FK "ツイートID"
        boolean is_read "既読フラグ"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }

    NotificationType {
        bigint id PK "ID"
        varchar name "通知タイプ名"
        varchar description "説明"
        timestamp created_at "作成日時"
        timestamp updated_at "更新日時"
    }
```


# 環境構築


## .envを作成し、以下を記載

SECRET_KEYは自身で生成する

[【Django】settings.pyのSECRET_KEYを再発行(リジェネレート)する](https://noauto-nolife.com/post/django-secret-key-regenerate/)

```.env
DATABASE_URL="postgres://postgres:postgres@db:5432/django_develop"
SECRET_KEY=<自身で生成したものを使う>
```

## dockerを立ち上げる

```
docker-compose up
```

ブラウザで[localhost:3000/hello](http://localhost:3000/hello)にアクセスし、以下の画面が表示されたら、構築完了。
![セットアップ完了後の画面](./static/setup_completed.png)
