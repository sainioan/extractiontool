from __future__ import unicode_literals
from django.db import models
import jsonfield
from django.views.generic import ListView


class Json_TableQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            obj.table.delete()
        super(Json_TableQuerySet, self).delete(*args, **kwargs)


class Json_Table(models.Model):
    user_id = models.IntegerField(null=True)
    pdf_id = models.IntegerField(null=True)
    page_number = models.IntegerField(null=True)
    table_num = models.IntegerField(null=True)
    json_table = models.JSONField()
    table = models.FileField(upload_to="json/", max_length=500)

    def delete(self, *args, **kwargs):
        self.table.delete()
        super(Json_Table, self).delete(*args, **kwargs)

