from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Department(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'department'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class FileInfo(models.Model):
    file_type = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    time = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'file_info'


class Meeting(models.Model):
    sponsor = models.ForeignKey('UserInfo', models.DO_NOTHING, db_column='sponsor', blank=True, null=True,related_name='sponsor')
    theme = models.CharField(max_length=255, blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)
    ratifier_field = models.ForeignKey('UserInfo', models.DO_NOTHING, db_column='ratifier\r\n_id', blank=True, null=True,related_name='ratifier')  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    time = models.DateTimeField(blank=True, null=True)
    meeting_type = models.ForeignKey('MeetingType', models.DO_NOTHING, blank=True, null=True)
    state = models.ForeignKey('MeetingState', models.DO_NOTHING, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)
    department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    is_approve = models.IntegerField(blank=True, null=True)
    approve_user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meeting'



class MeetingAnswer(models.Model):
    answer = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meeting_answer'


class MeetingState(models.Model):
    state = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meeting_state'


class MeetingType(models.Model):
    meeting_type_id = models.AutoField(primary_key=True)
    meeting_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meeting_type'


class MeetingUserRelation(models.Model):
    meeting = models.ForeignKey(Meeting, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UserInfo', models.DO_NOTHING, blank=True, null=True)
    answer = models.ForeignKey(MeetingAnswer, models.DO_NOTHING, blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    answer_0 = models.CharField(db_column='answer', max_length=255, blank=True, null=True)  # Field renamed because of name conflict.
    answer_remake = models.CharField(max_length=255, blank=True, null=True)
    is_sign = models.IntegerField(blank=True, null=True)
    time_sign = models.TimeField(blank=True, null=True)
    place_sign = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meeting_user_relation'


class ObserPartyRelation(models.Model):
    observation = models.ForeignKey('ObservationList', models.DO_NOTHING, blank=True, null=True)
    party = models.ForeignKey('PartyBranch', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'obser_party_relation'


class ObserRoleRelation(models.Model):
    observation = models.ForeignKey('ObservationList', models.DO_NOTHING, blank=True, null=True)
    role = models.ForeignKey('RoleInfo', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'obser_role_relation'


class ObservationList(models.Model):
    observation_point = models.CharField(max_length=255, blank=True, null=True)
    pid = models.ForeignKey('self', models.DO_NOTHING, db_column='pid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'observation_list'


class Overtime(models.Model):
    id = models.IntegerField(primary_key=True)
    day_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'overtime'




class PartyBranch(models.Model):
    party_branch = models.CharField(max_length=255, blank=True, null=True)
    pid = models.ForeignKey('self', models.DO_NOTHING, db_column='pid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_branch'


class PartyUserRelation(models.Model):
    user = models.ForeignKey('UserInfo', models.DO_NOTHING, blank=True, null=True)
    party_branch = models.ForeignKey(PartyBranch, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_user_relation'


class ProgressType(models.Model):
    progress_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'progress_type'


class RespList(models.Model):
    content = models.CharField(max_length=255, blank=True, null=True)
    pid = models.ForeignKey('self', models.DO_NOTHING, db_column='pid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resp_list'


class RespPartyRelation(models.Model):
    resp = models.ForeignKey(RespList, models.DO_NOTHING, blank=True, null=True)
    party = models.ForeignKey(PartyBranch, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resp_party_relation'


class RespRoleRelation(models.Model):
    resp = models.ForeignKey(RespList, models.DO_NOTHING, blank=True, null=True)
    role = models.ForeignKey('RoleInfo', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resp_role_relation'


class RoleInfo(models.Model):
    role = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role_info'


class RoleUserRelation(models.Model):
    user = models.ForeignKey('UserInfo', models.DO_NOTHING, blank=True, null=True)
    role = models.ForeignKey(RoleInfo, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role_user_relation'


class Task(models.Model):
    content = models.CharField(max_length=255, blank=True, null=True)
    pid = models.ForeignKey('self', models.DO_NOTHING, db_column='pid', blank=True, null=True)
    department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    state = models.ForeignKey('TaskState', models.DO_NOTHING, blank=True, null=True)
    source = models.ForeignKey('TaskSource', models.DO_NOTHING, blank=True, null=True)
    type = models.ForeignKey('TaskType', models.DO_NOTHING, blank=True, null=True)
    priority = models.ForeignKey('TaskPriority', models.DO_NOTHING, blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)
    appointor = models.ForeignKey('UserInfo', models.DO_NOTHING, blank=True, null=True)
    end_time = models.DateField(blank=True, null=True)
    start_time = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task'


class TaskAnnex(models.Model):
    annex_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_annex'


class TaskAnnexRelation(models.Model):
    task = models.ForeignKey(Task, models.DO_NOTHING, blank=True, null=True)
    task_prog_record = models.ForeignKey('TaskProgRecord', models.DO_NOTHING, blank=True, null=True)
    annex = models.ForeignKey(TaskAnnex, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_annex_relation'


class TaskJurisdiction(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    department_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_jurisdiction'


class TaskMessRecord(models.Model):
    task = models.ForeignKey(Task, models.DO_NOTHING, blank=True, null=True)
    oper_user = models.ForeignKey('UserInfo', models.DO_NOTHING, blank=True, null=True,related_name='oper')
    noti_user = models.ForeignKey('UserInfo', models.DO_NOTHING, blank=True, null=True,related_name='noti')
    type = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_mess_record'


class TaskPriority(models.Model):
    priority = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_priority'


class TaskProgRecord(models.Model):
    task = models.ForeignKey(Task, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UserInfo', models.DO_NOTHING, blank=True, null=True)
    progress_type = models.ForeignKey(ProgressType, models.DO_NOTHING, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    is_baomi = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_prog_record'


class TaskSource(models.Model):
    source = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_source'


class TaskState(models.Model):
    state = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_state'


class TaskType(models.Model):
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_type'


class TaskUserRelation(models.Model):
    user = models.ForeignKey('UserInfo', models.DO_NOTHING, blank=True, null=True)
    task = models.ForeignKey(Task, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task_user_relation'


class UserInfo(models.Model):
    department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    job_id = models.CharField(max_length=11, blank=True, null=True)
    is_ratifier = models.IntegerField(blank=True, null=True)
    vx_code = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_info'
