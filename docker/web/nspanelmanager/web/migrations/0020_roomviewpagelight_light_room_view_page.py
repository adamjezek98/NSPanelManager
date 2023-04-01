# Generated by Django 4.1.7 on 2023-04-01 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0019_nspanel_online_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomViewPageLight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_position', models.IntegerField(default=0)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.room')),
            ],
        ),
        migrations.AddField(
            model_name='light',
            name='room_view_page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web.roomviewpagelight'),
        ),
    ]
