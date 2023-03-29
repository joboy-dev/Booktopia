from django.db import models

from user.models import CustomUser

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=128, null=False)
    description = models.CharField(max_length=5000, null=False)
    book_file = models.FileField(upload_to='books', null=False)
    author = models.ManyToManyField(CustomUser, related_name='authors', max_length=4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} -- {self.author.last_name} {self.author.first_name}'
