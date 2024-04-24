from django.db import models

# Create your models here.
class Member(models.Model):
     mId = models.CharField(max_length=50, primary_key=True, unique=True)
     username = models.CharField(max_length=50,unique=True)
     gender= models.CharField(max_length=50)
     email = models.CharField(max_length=50)
     pId = models.CharField(max_length=50,unique=True)

     class Meta:
        db_table = 'Member'

