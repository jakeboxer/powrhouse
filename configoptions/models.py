from django.db import models

class ConfigOptionManager (models.Manager):
    """
    Encapsulates the querying of configuration options.
    Correct usage:
    my_int = ConfigOption.vals.get('my_int', type=int, default=42)
    """
    def get (self, slug, **kwargs):
        try:
            qset = super(ConfigOptionManager, self).get_query_set()
            config_obj = qset.get(slug=slug)
            config_val = config_obj.value
        except ConfigOption.DoesNotExist:
            if 'default' in kwargs:
                config_val = kwargs['default']
            else:
                err = "The option with slug '%s' does not exist." % slug
                raise ConfigOption.DoesNotExist(err)

        if 'type' in kwargs:
            try:
                config_val = kwargs['type'](config_val)
            except ValueError:
                err = "The option with slug '%s' isn't %s" % \
                    (slug, kwargs['type'])
                raise ValueError(err)

        return config_val

class ConfigOption (models.Model):
    slug    = models.SlugField(max_length=255, unique=True)
    value   = models.TextField()

    objects = models.Manager()
    vals    = ConfigOptionManager()

    def __unicode__ (self):
        return "%s = '%s'" % (self.slug, self.value,)