from django.conf import settings
from django.db import models
from django.shortcuts import resolve_url
from django.utils import timezone
import markdown
from markdown.extensions import Extension


class Tag(models.Model):
    name = models.CharField('タグ名', max_length=255, unique=True)

    def __str__(self):
        # 検索フォーム等では、紐づいた記事数を表示する。その場合はpost_countという属性に記事数を持つ。
        if hasattr(self, 'post_count'):
            return f'{self.name}({self.post_count})'
        else:
            return self.name


class Post(models.Model):
    """記事"""
    title = models.CharField('タイトル', max_length=32)
    text = models.TextField('本文')
    tags = models.ManyToManyField(Tag, verbose_name='タグ', blank=True)
    relation_posts = models.ManyToManyField('self', verbose_name='関連記事', blank=True)
    is_public = models.BooleanField('公開可能か?', default=True)
    description = models.TextField('記事の説明', max_length=130)
    keywords = models.CharField('記事のキーワード', max_length=255, default='Python,Django')
    created_at = models.DateTimeField('作成日', default=timezone.now)
    updated_at = models.DateTimeField('更新日', default=timezone.now)

    def __str__(self):
        return self.title

    def browser_push(self):
        """記事をブラウザ通知"""
        if settings.USE_ONE_SIGNAL:
            import requests
            data = {
                'app_id': settings.ONE_SIGNAL_APP_ID,
                'included_segments': ['All'],
                'contents': {'en': self.title},
                'headings': {'en': 'ブログ'},
            }
            requests.post(
                "https://onesignal.com/api/v1/notifications",
                headers={'Authorization': settings.ONE_SIGNAL_REST_KEY},
                json=data,
            )

    def text_to_html(self):
        return markdown.markdown(self.text, extensions=['markdown.extensions.extra', 'markdown.extensions.toc'])


class Comment(models.Model):
    """記事に紐づくコメント"""
    name = models.CharField('名前', max_length=255, default='名無し')
    text = models.TextField('本文')
    target = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='対象記事')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.text[:20]

    def text_to_html(self):
        return markdown.markdown(self.text, extensions=['markdown.extensions.extra', 'markdown.extensions.toc', EscapeHtml()])


class Reply(models.Model):
    """コメントに紐づく返信"""
    name = models.CharField('名前', max_length=255, default='名無し')
    text = models.TextField('本文')
    target = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='対象コメント')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.text[:20]

    def text_to_html(self):
        return markdown.markdown(self.text, extensions=['markdown.extensions.extra', 'markdown.extensions.toc', EscapeHtml()])


class EscapeHtml(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')
