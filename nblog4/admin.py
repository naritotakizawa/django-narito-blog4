from django import forms
from django.urls import reverse_lazy
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
    extra = 5


class CommentAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]


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
admin.site.register(Reply)
admin.site.register(Tag)
