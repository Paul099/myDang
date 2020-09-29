# Generated by Django 2.2 on 2020-09-29 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_authgrouppermissions_authpermission_authuser_authusergroups_authuseruserpermissions_department_djang'),
    ]

    operations = [
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
        migrations.AlterModelOptions(
            name='meeting',
            options={},
        ),
    ]
