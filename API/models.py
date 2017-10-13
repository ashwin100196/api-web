from django.db import models

# Create your models here.

from datetime import datetime

from django.db.models.fields import DateTimeField

class UCDateTimeField(DateTimeField):

    def pre_save(self, model_instance, add):
        if self.auto_now or (self.auto_now_add and add):
            value = datetime.datetime.now()
            setattr(model_instance, self.attname, value)
            return value
        else:
            value = getattr(model_instance, self.attname)
            if not isinstance(value, datetime):
                # assume that the value is a timestamp if it is not a datetime
                value = datetime.fromtimestamp(int(value))
                # an exception might be better than an assumption
                setattr(model_instance, self.attname, value)
            return super(UCDateTimeField, self).pre_save(model_instance, add)

class Alert(models.Model):
    timestamp = UCDateTimeField()
    event_type = models.CharField(max_length=100, blank=True, default='person')
    condition = models.CharField(max_length=100,blank=True, default='False')
    alert = models.CharField(max_length=100,blank = True, default = 'True')

    class Meta:
        ordering = ('timestamp',)
	