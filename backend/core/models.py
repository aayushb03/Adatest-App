import uuid

from django.db import models


# Create your models here.

class Test(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    session_id = models.CharField(max_length=50, default="unknown")
    title = models.TextField()
    topic = models.CharField(max_length=50)
    validity = models.CharField(max_length=50, default="unapproved")
    label = models.CharField(max_length=20, default="unacceptable")
    ground_truth = models.CharField(max_length=20, default="unknown")


class Log(models.Model):
    session_id = models.CharField(max_length=50, default="unknown")
    test_ids = models.TextField()
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    

class Perturbation(models.Model): 
    test_parent = models.ForeignKey(Test, on_delete=models.CASCADE)
    label = models.CharField(max_length=20, default="unacceptable")
    id = models.UUIDField(max_length=50, default=uuid.uuid4, editable=False, primary_key=True)
    session_id = models.CharField(max_length=50, default="unknown")
    title = models.TextField()
    type = models.CharField(max_length=20, default="spelling")
    topic = models.CharField(max_length=50)
    validity = models.CharField(max_length=50, default="unapproved")
    ground_truth = models.CharField(max_length=20, default="unknown")


