from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from user.models import CustomUser

# Create your models here.
class Book(models.Model):
    '''Book model'''

    title = models.CharField(max_length=128, null=False)
    description = models.CharField(max_length=5000, null=False)
    book_file = models.FileField(upload_to='books', null=False)
    book_cover_picture = models.ImageField(default='book_pics/default.jpg',upload_to='book_pics')
    author = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    no_of_comments = models.IntegerField(null=False, default=0)
    no_of_ratings = models.IntegerField(null=False, default=0)
    average_rating = models.DecimalField(null=False, decimal_places=2, max_digits=3, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} | {self.author.first_name}, {self.author.last_name}'

    class Meta:
        ordering = ['-updated']


class Comment(models.Model):
    '''Comments model'''

    commenter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    comment = models.CharField(max_length=5000, null=False)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.commenter.email} | {str(self.rating)}'
    
    class Meta:
        ordering = ['-updated']






# author = models.ManyToManyField(CustomUser, related_name='authors', max_length=4)
# author = models.ManyToManyField(through='BookAuthor', related_name='authors', max_length=4)
