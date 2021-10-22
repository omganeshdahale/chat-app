# Generated by Django 3.2.8 on 2021-10-21 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_chatgroup_chatgroupinvite'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatgroupinvite',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterField(
            model_name='chatgroup',
            name='description',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='chatgroupinvite',
            name='uses',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
