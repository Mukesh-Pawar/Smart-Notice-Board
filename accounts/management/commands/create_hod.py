from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from accounts.models import User


class Command(BaseCommand):
    help = 'Create or update an HOD / Super Admin account securely.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--name', required=True)
        parser.add_argument('--department', default='Department')
        parser.add_argument('--mobile', default='')
        parser.add_argument('--password', help='Optional password; if omitted Django prompts securely.')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        try:
            validate_email(email)
        except ValidationError as exc:
            raise CommandError(f'Invalid email: {exc}')
        password = options.get('password')
        if not password:
            from getpass import getpass
            password = getpass('HOD password: ')
            confirm = getpass('Confirm HOD password: ')
            if password != confirm:
                raise CommandError('Passwords do not match.')
        user, created = User.objects.get_or_create(email=email, defaults={
            'full_name': options['name'],
            'department': options['department'],
            'mobile': options['mobile'],
            'role': User.Role.HOD,
            'status': User.Status.ACTIVE,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        })
        user.full_name = options['name']
        user.department = options['department']
        user.mobile = options['mobile']
        user.role = User.Role.HOD
        user.status = User.Status.ACTIVE
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'HOD account {"created" if created else "updated"}: {email}'))
