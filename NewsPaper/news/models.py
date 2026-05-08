from django.db import models
from django.contrib.auth.models import User
from django.db.models import OneToOneField, ForeignKey, ManyToManyField
from django.db.models.deletion import CASCADE
from django.db.models import Sum

article = 'AR'
news = 'NW'
POSITIONS = [
    (article, 'Статья'),
    (news, 'Новость'),
]

class RatingMixin:
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class Author(models.Model):
    user = OneToOneField(User, on_delete = models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        from .models import Comment
        posts_sum = self.post_set.aggregate(res = Sum('rating'))['res'] or 0
        sum_author_comments = self.user.comment_set.aggregate(res=Sum('rating'))['res'] or 0
        sum_comments = Comment.objects.filter(post__author=self).aggregate(res=Sum('rating'))['res'] or 0
        update = ((posts_sum*3) + sum_author_comments + sum_comments)
        self.rating = update
        self.save()


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)

class Post(models.Model, RatingMixin):
    author = ForeignKey(Author, on_delete = models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POSITIONS, default=article)
    created = models.DateTimeField(auto_now_add=True)
    heading = models.CharField(max_length=100)
    body = models.TextField()
    rating = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, through='PostCategory')

    def preview(self):
        return self.body[:124] + '...'

class PostCategory(models.Model):
    post = ForeignKey('Post', on_delete=models.CASCADE)
    category = ForeignKey('Category', on_delete=models.CASCADE)

class Comment(models.Model, RatingMixin):
    post = ForeignKey('Post', on_delete=models.CASCADE)
    user = ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

