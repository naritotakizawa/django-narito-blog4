from django import forms
from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import Post, Comment, Reply, Tag


class SuggestPostWidget(forms.SelectMultiple):
    template_name = 'nblog4/widgets/suggest.html'

    class Media:
        css = {
            'all': [
                'nblog4/css/admin_post_form.css',

            ]
        }
        js = ['nblog4/js/suggest.js']

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' suggest'
        else:
            self.attrs['class'] = 'suggest'


class AdminPostCreateForm(forms.ModelForm):
    """記事の作成・更新フォーム"""

    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': '[TOC]\n\n## 概要\nこんな感じで'}),
            'relation_posts': SuggestPostWidget(attrs={'data-url': reverse_lazy('nblog4:post-simple-search')}),
        }


class ReplyInline(admin.StackedInline):
    model = Reply


class ReplyAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'name', 'short_text', 'comment_url', 'post_url']
    list_filter = ['name']
    ordering = ['-created_at']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('target', 'target__target')

    def short_text(self, instance):
        return instance.text[:100]

    def comment_url(self, obj):
        url = resolve_url('admin:nblog4_comment_change', object_id=obj.target.pk)
        tag = f'<a href="{url}" target="_blank">{obj.target.pk}</a>'
        return mark_safe(tag)

    def post_url(self, obj):
        url = settings.BLOG4_DETAIL_URL.format(obj.target.target.pk)
        tag = f'<a href="{url}" target="_blank">{obj.target.target.title}</a>'
        return mark_safe(tag)


class CommentAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]
    list_display = ['created_at', 'name', 'short_text', 'target', 'url']
    list_filter = ['name']
    ordering = ['-created_at']

    def short_text(self, instance):
        return instance.text[:100]

    def url(self, obj):
        url = settings.BLOG4_DETAIL_URL.format(obj.target.pk)
        tag = f'<a href="{url}" target="_blank">{obj.target.title}</a>'
        return mark_safe(tag)

def notify(modeladmin, request, queryset):
    for post in queryset:
        post.browser_push()
notify.short_description = '通知を送信する'


class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'text')
    list_display = ['title', 'is_public', 'updated_at', 'created_at']
    list_filter = ['is_public', 'tags', 'created_at', 'updated_at']
    form = AdminPostCreateForm
    actions = [notify]


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Tag)
