from django.db import models
from django.db.models import SubfieldBase, CharField
from django.forms.fields import ChoiceField
from django.conf import settings as s
from os import listdir, path


# http://www.djangosnippets.org/snippets/562/#c673
class QuerySetManager(models.Manager):
    use_for_related_fields = True
    def __init__(self, qs_class=models.query.QuerySet):
        self.queryset_class = qs_class
        super(QuerySetManager, self).__init__()

    def get_query_set(self):
        return self.queryset_class(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args) 

class QuerySet(models.query.QuerySet):
    """
    Base QuerySet class for adding custom methods that are made
    available on both the manager and subsequent cloned QuerySets.
    """
    @classmethod
    def as_manager(cls, ManagerClass=QuerySetManager):
        return ManagerClass(cls) 


class MediaList(list):

    def __init__(self, list=[], dir=s.MEDIA_ROOT+'/graphlib'):
        super(MediaList, self).__init__(list)
        self.dir = dir

    def _make_html_import(self, full_src):
        """Create HTML <script> tag."""
        IMPORT_TEMP = '<script src="%s"></script>'
        return IMPORT_TEMP % full_src

    def _list_available(self):
        return listdir(s.MEDIA_ROOT+'graphlib')        

    def _get_full_url(self, src):
        return s.MEDIA_ROOT+'graphlib/' + src

    def _get_media_url(self, src):
        return s.MEDIA_URL+'graphlib/' + src

    def _walk(self):
        """
        Walk on chosen files and return a generator of chosen files.
        """
        for f in self:
            full_src = s.MEDIA_ROOT+'graphlib/'+f
            media_src = s.MEDIA_URL+'graphlib/'+f
            # Don't treat non-existing
            if not path.exists(full_src):
                continue
            # Yield files
            elif not path.isdir(full_src):
                yield media_src
            # Search in directory
            else:
                for subfile_name in listdir(full_src):
                    sf = full_src + '/' + subfile_name
                    if not path.isfile(sf):
                        continue
                    elif path.exists(sf):
                        yield media_src + '/' + subfile_name

    def sources(self):
        """Return list of files' URL."""
        return [ s for s in self._walk() ] 

    def file_names(self):
        return [ path.basename(s) for s in self._walk() ] 

    def get_source_and_name(self):
        return [ (s,path.basename(s)) for s in self._walk() ] 

    def htmlize(self):
        """
        Return an generator of HTML <script> tag of all of
        files chosen.
        Can search files in one subdirectory.
        """
        return [ self._make_html_import(s) for s in self._walk() ]


class MediaField(CharField):
    """
    Custom Field which saves chosen from MEDIA_ROOT.
    Choices are media files and stored as splited string.
    """
    
    description = "A choice of files in media"
    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2000 # Why not ?
        super(MediaField, self).__init__(*args, **kwargs)
        # choices are MEDIA_ROOT
        self._choices = [ (x,x) for x in listdir(s.MEDIA_ROOT+'graphlib') ]

    def to_python(self, value):
        """From VARCHAR to MediaList()."""
        if not value:
            return MediaList()
        if isinstance(value, basestring):
            return MediaList(value.split())
        elif isinstance(value, (list,tuple)):
            return MediaList(value)

    def validate(self, value, model_instance):
        # TODO : Make validation
        return

    def get_prep_value(self, value):
        """From list() to string."""
        return ' '.join(value)

    def formfield(self, **kwargs):
        """Automaticaly uses ChoiceField."""
        kwargs['choices'] = self.choices
        return ChoiceField(**kwargs)
