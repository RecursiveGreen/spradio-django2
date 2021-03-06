# Generated by Django 2.0 on 2018-01-05 19:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='added on')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('disabled', models.BooleanField(default=False, verbose_name='disabled state')),
                ('disabled_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='disabled on')),
                ('disabled_reason', models.TextField(blank=True, verbose_name='reason for disabling')),
                ('published_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='published for listening')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='title')),
                ('sorted_title', models.CharField(db_index=True, editable=False, max_length=255, verbose_name='naturalized title')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='added on')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('disabled', models.BooleanField(default=False, verbose_name='disabled state')),
                ('disabled_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='disabled on')),
                ('disabled_reason', models.TextField(blank=True, verbose_name='reason for disabling')),
                ('published_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='published for listening')),
                ('alias', models.CharField(blank=True, max_length=127, verbose_name='alias')),
                ('first_name', models.CharField(blank=True, max_length=127, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=127, verbose_name='last name')),
                ('sorted_full_name', models.CharField(db_index=True, editable=False, max_length=255, verbose_name='naturalized full name')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='added on')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('disabled', models.BooleanField(default=False, verbose_name='disabled state')),
                ('disabled_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='disabled on')),
                ('disabled_reason', models.TextField(blank=True, verbose_name='reason for disabling')),
                ('published_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='published for listening')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='title')),
                ('sorted_title', models.CharField(db_index=True, editable=False, max_length=255, verbose_name='naturalized title')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='added on')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('disabled', models.BooleanField(default=False, verbose_name='disabled state')),
                ('disabled_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='disabled on')),
                ('disabled_reason', models.TextField(blank=True, verbose_name='reason for disabling')),
                ('published_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='published for listening')),
                ('song_type', models.CharField(choices=[('J', 'Jingle'), ('S', 'Song')], default='S', max_length=1, verbose_name='song type')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('num_played', models.PositiveIntegerField(default=0, verbose_name='number of times played')),
                ('last_played', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='was last played')),
                ('length', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='song length (in seconds)')),
                ('path', models.TextField(verbose_name='absolute path to song file')),
                ('sorted_title', models.CharField(db_index=True, editable=False, max_length=255, verbose_name='naturalized title')),
                ('album', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='radio.Album')),
                ('artists', models.ManyToManyField(blank=True, to='radio.Artist')),
                ('game', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='radio.Game')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
