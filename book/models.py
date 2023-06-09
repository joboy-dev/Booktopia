from django.db import models

from user.models import CustomUser

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=128, null=False)
    description = models.CharField(max_length=5000, null=False)
    book_file = models.FileField(upload_to='books', null=False)
    book_cover_picture = models.ImageField(default='book_pics/default.jpg',upload_to='book_pics')
    # author = models.ManyToManyField(CustomUser, related_name='authors', max_length=4)
    # author = models.ManyToManyField(through='BookAuthor', related_name='authors', max_length=4)
    author = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} -- {self.author.first_name}, {self.author.last_name}'

# class BookAuthor(models.Model):
#     book = models.ForeignKey(Book, null=False, on_delete=models.CASCADE)
#     author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL)
