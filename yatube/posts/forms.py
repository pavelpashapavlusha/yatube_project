from xml.etree.ElementTree import Comment

from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_subject(self):
        text = self.cleaned_data['text']
        if not text:
            raise forms.ValidationError(
                'Вы должны обязательно что-то написать',
                params={'text': text},
            )
        return text
