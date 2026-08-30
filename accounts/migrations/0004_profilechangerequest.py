from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_user_profile_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileChangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_full_name', models.CharField(max_length=120)),
                ('requested_email', models.EmailField(max_length=254)),
                ('requested_mobile', models.CharField(blank=True, max_length=15)),
                ('requested_department', models.CharField(blank=True, max_length=120)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], db_index=True, default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('review_note', models.CharField(blank=True, max_length=255)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_profile_requests', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_change_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', 'status'], name='accounts_pr_user_id_8a0e35_idx'),
                    models.Index(fields=['status', 'created_at'], name='accounts_pr_status_2e2b72_idx'),
                ],
            },
        ),
    ]
