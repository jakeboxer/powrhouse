from django.contrib.auth.models import Permission

perm_names = ('add_household','change_household','delete_household')
perms = list(Permission.objects.filter(codename__in=perm_names))