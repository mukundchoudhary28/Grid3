# Generated by Django 3.2.5 on 2021-07-24 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gridapp', '0005_auto_20210723_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='ADDomain',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='response',
            name='Workgroup',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='response',
            name='DomainInfo',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
