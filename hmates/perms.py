from django.contrib.auth.models import Permission

perm_names = ('add_housemate','change_housemate','delete_housemate')
perms = list(Permission.objects.filter(codename__in=perm_names))