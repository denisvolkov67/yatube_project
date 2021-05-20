from django.contrib.auth import get_user_model
from django.db import models

from .validators import validate_not_empty

User = get_user_model()


class Post(models.Model):
    text = models.TextField(validators=[validate_not_empty])
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey('Group', on_delete=models.SET_NULL,
                              related_name='posts', blank=True, null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title