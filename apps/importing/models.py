import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


@python_2_unicode_compatible
class Provider(models.Model):
    """
    Provider of dataset, used for semi-authentication purposes
    """
    name = models.CharField(max_length=128, unique=True)
    code = models.SlugField(max_length=32, unique=True)
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    def url(self):
        if self.pk is not None:
            url = reverse(
                'importing:provider',
                kwargs={
                    'code': self.code,
                    'token': str(self.token),
                    'file_name': "data",
                    'ext': "xml",
                }
            )
            return format_html(
                '<a href={url}>{url}</span>',
                url=url,
            )
        else:
            return "-"
    url.short_description = "example URL for provider"

    def __str__(self):
        return force_text(u"{name} <{code}>".format(name=self.name, code=self.code))


@python_2_unicode_compatible
class ProviderLog(models.Model):
    """
    Provider Log entry that corresponds with every entry (POST Request) that is sent to the server
    """
    provider = models.ForeignKey(
        Provider,
        on_delete=models.DO_NOTHING,
    )
    is_valid = models.BooleanField(default=False)
    content_type = models.CharField(max_length=32, default="application/txt")
    body = models.TextField(null=False, blank=True)
    file_name = models.CharField(max_length=32)
    file_path = models.CharField(max_length=256)
    ext = models.CharField(max_length=16)
    received_time = models.DateTimeField(default=timezone.now)
    uuid4 = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    last_processed = models.DateTimeField(null=True, blank=True, default=None)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return force_text(u"{provider} | <{received}>".format(provider=self.provider, received=self.received_time))

    def is_processed(self):
        return self.last_processed is not None
    is_processed.short_description = "Was the Log already processed?"

    def parsed_body(self):
        # noinspection PyPep8Naming
        from bs4 import BeautifulSoup as bs
        import html
        x = bs(self.body)
        return mark_safe("<pre>"+html.escape(x.prettify())+"</pre>")


class ReadonlyProviderLog(ProviderLog):
    class Meta:
        proxy = True
