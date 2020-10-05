# Generated by Django 2.2 on 2020-09-29 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liweb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'meeting_state',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MeetingType',
            fields=[
                ('meeting_type_id', models.AutoField(primary_key=True, serialize=False)),
                ('meeting_type', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'meeting_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RespPartyRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'resp_party_relation',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='RespDepRelation',
        ),
    ]