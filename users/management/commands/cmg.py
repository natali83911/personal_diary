from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создаёт группу модераторов с разрешением view_user и добавляет пользователя"

    def handle(self, *args, **options):
        User = get_user_model()
        email = "moderator@example.com"
        password = "123"

        # Создаем или получаем группу "moderators"
        group, created = Group.objects.get_or_create(name="moderators")

        # Получаем разрешение на просмотр пользователей
        content_type = ContentType.objects.get_for_model(User)
        view_perm = Permission.objects.get(
            codename="view_user", content_type=content_type
        )
        group.permissions.add(view_perm)

        # Создаем пользователя (если такого еще нет)
        user, created_user = User.objects.get_or_create(email=email)
        if created_user:
            user.set_password(password)
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Пользователь {email} создан."))
        else:
            self.stdout.write(f"Пользователь {email} уже существует.")

        # Добавляем пользователя в группу
        user.groups.add(group)
        self.stdout.write(
            self.style.SUCCESS(f'Пользователь {email} добавлен в группу "moderators"')
        )
        self.stdout.write(self.style.SUCCESS(f"Пароль для входа: {password}"))
