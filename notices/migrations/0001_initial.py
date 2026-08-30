# Generated manually to keep the project self-contained.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('accounts', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('priority', models.CharField(choices=[('NORMAL', 'Normal'), ('IMPORTANT', 'Important'), ('EMERGENCY', 'Emergency')], db_index=True, default='NORMAL', max_length=20)),
                ('start_time', models.DateTimeField(db_index=True)),
                ('expiry_time', models.DateTimeField(db_index=True)),
                ('duration_minutes', models.PositiveIntegerField(default=60)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('SCHEDULED', 'Scheduled'), ('ACTIVE', 'Active'), ('EXPIRED', 'Expired'), ('CANCELLED', 'Cancelled')], db_index=True, default='DRAFT', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='notices', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-start_time', '-created_at'], 'indexes': [models.Index(fields=['status', 'start_time', 'expiry_time'], name='notices_not_status_3d1d6a_idx'), models.Index(fields=['priority', 'status'], name='notices_not_priorit_0a0a1b_idx')]},
        ),
        migrations.CreateModel(
            name='NoticeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('CREATED', 'Created'), ('UPDATED', 'Updated'), ('DELETED', 'Deleted'), ('CANCELLED', 'Cancelled'), ('REDISPLAYED', 'Redisplayed'), ('ACTIVATED', 'Activated'), ('EXPIRED', 'Expired')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.CharField(blank=True, max_length=255)),
                ('notice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logs', to='notices.notice')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notice_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-timestamp'], 'indexes': [models.Index(fields=['notice', '-timestamp'], name='notices_not_notice__0d6b15_idx'), models.Index(fields=['user', '-timestamp'], name='notices_not_user_id_75cf67_idx')]},
        ),
    ]
