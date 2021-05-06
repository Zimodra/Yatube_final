from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(
        "Group", on_delete=models.SET_NULL,
        related_name="posts", blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        result = f"{self.author} - {self.pub_date} - {self.text[:15]}"
        return result

    class Meta:
        ordering = ['-pub_date']


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200,
        help_text='Дайте короткое название заголовку'
    )
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name=["unique user_author"]
            )
        ]
