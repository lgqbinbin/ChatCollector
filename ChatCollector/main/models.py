from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    profile = models.TextField()

    def __str__(self):
        return self.username


class TimeRecord(models.Model):
    table_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.table_name} ({self.start_time} - {self.end_time})"

    class Meta:
        db_table = 'time_record'