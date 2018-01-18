# Generated by Django 2.0 on 2018-01-18 17:36

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('radio', '0002_naming_and_sorting'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RadioProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='added on')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('favorites', models.ManyToManyField(related_name='song_favorites', to='radio.Song')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='added on')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('value', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='song rating')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_profile', to='profiles.RadioProfile')),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='radio.Song')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SongRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='added on')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('queued_at', models.DateTimeField(blank=True, default=None, null=True, verbose_name='song queued at')),
                ('played_at', models.DateTimeField(blank=True, default=None, null=True, verbose_name='song played at')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='request_profile', to='profiles.RadioProfile')),
                ('song', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='radio.Song')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='radioprofile',
            name='ratings',
            field=models.ManyToManyField(related_name='song_ratings', through='profiles.Rating', to='radio.Song'),
        ),
        migrations.AddField(
            model_name='radioprofile',
            name='song_requests',
            field=models.ManyToManyField(related_name='song_requests', through='profiles.SongRequest', to='radio.Song'),
        ),
        migrations.AddField(
            model_name='radioprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
