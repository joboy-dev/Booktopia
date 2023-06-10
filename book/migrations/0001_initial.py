# Generated by Django 4.1.7 on 2023-06-09 21:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=5000)),
                ('book_file', models.FileField(upload_to='books')),
                ('book_cover_picture', models.ImageField(default='book_pics/default.jpg', upload_to='book_pics')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('author', models.ManyToManyField(max_length=4, related_name='authors', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]