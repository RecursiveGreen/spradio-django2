# Generated by Django 2.2.1 on 2019-06-06 19:06

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import radio.fields


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0003_song_next_play'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='added on')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('iri', radio.fields.RadioIRIField(verbose_name='IRI path to song file')),
                ('mime_type', models.CharField(blank=True, max_length=64, verbose_name='file MIME type')),
                ('file_size', models.BigIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='file size')),
                ('length', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='song length (in seconds)')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='song',
            name='length',
        ),
        migrations.RemoveField(
            model_name='song',
            name='path',
        ),
        migrations.AddField(
            model_name='song',
            name='active_store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_for', to='radio.Store'),
        ),
        migrations.AddField(
            model_name='song',
            name='stores',
            field=models.ManyToManyField(blank=True, related_name='song', to='radio.Store'),
        ),
    ]
