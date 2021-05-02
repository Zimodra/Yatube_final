from django import forms
from .models import Post, Comment
from django.utils.translation import ugettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'group': _('Сообщество:'),
            'text': _('Текст:'),
            'image': _('Изображение:')
        }
        error_messages = {
            'text': {'required': 'Поле Текст не может быть пустым'}
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Комментарий:')
        }
        widgets = {'text': forms.Textarea(
            attrs={'rows': 6, 'cols': 93}
        )}
