# Generated by Django 5.1.2 on 2024-12-18 11:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tweets", "0005_alter_tweet_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tweet",
            name="content",
            field=models.CharField(max_length=140, verbose_name="ツイート内容"),
        ),
    ]
