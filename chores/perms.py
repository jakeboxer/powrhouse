from django.contrib.auth.models import Permission

perm_names = ('add_chore','change_chore','delete_chore')
perms = list(Permission.objects.filter(codename__in=perm_names))