# Generated by Django 4.1.7 on 2023-05-21 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0029_rename_name_scene_friendly_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scene',
            name='lights',
        ),
        migrations.CreateModel(
            name='LightState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color_mode', models.CharField(default='dimmer', max_length=32)),
                ('light_level', models.IntegerField(default=0)),
                ('hue', models.IntegerField(default=0)),
                ('saturation', models.IntegerField(default=0)),
                ('light', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.light')),
                ('scene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.scene')),
            ],
        ),
    ]