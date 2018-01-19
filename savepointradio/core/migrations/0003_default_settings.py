# Generated by Django 2.0 on 2017-12-28 15:16

from django.db import migrations, models


def default_settings(apps, schema_editor):
    SETTING_TYPES = { 'Integer': 0, 'Float': 1, 'String': 2, 'Bool': 3 }
    Setting = apps.get_model('core', 'Setting')
    db_alias = schema_editor.connection.alias
    Setting.objects.using(db_alias).bulk_create([
        Setting(name='max_song_requests',
                description='The maximum amount of requests a user can have '
                            'queued at any given time. This restriction does '
                            'not apply to users who are designated as staff.',
                setting_type=SETTING_TYPES['Integer'],
                data='5'),
        Setting(name='replay_ratio',
                description='This defines how long before a song can be '
                            'played/requested again once it\'s been played. '
                            'The ratio is based on the total song length of '
                            'all the enabled, requestable songs in the radio '
                            'playlist. Example: If the total song length of '
                            'the radio playlist is 432000 seconds (5 days), '
                            'then a ratio of 0.75 will mean that a song cannot '
                            'be played again for 324000 seconds (0.75 * 432000 '
                            '= 324000 seconds = 3 days, 18 hours).',
                setting_type=SETTING_TYPES['Float'],
                data='0.75'),
        Setting(name='songs_per_jingle',
                description='The amount of songs that will be played between '
                            'jingles.',
                setting_type=SETTING_TYPES['Integer'],
                data='30'),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_create_dj_user'),
    ]

    operations = [
        migrations.RunPython(default_settings),
    ]
