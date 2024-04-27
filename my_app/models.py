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

class House(models.Model):
     hId = models.CharField(max_length=100, primary_key=True, unique=True, default="TW")

     status = models.IntegerField(default=0)
     title = models.CharField(max_length=1000)
     region = models.IntegerField(default=00)

     class Meta:
        db_table = 'House'
class Equipment(models.Model):
     hId = models.OneToOneField(House,primary_key=True,on_delete=models.PROTECT,to_field='hId',auto_created=False)
     sofa = models.IntegerField(default=0)
     tv = models.IntegerField(default=0)
     wash_machine = models.IntegerField(default=0)
     wifi = models.IntegerField(default=0)
     bed = models.IntegerField(default=0)
     refrigerator = models.IntegerField(default=0)
     hotwater = models.IntegerField(default=0)
     channel4 = models.IntegerField(default=0)
     cabinet = models.IntegerField(default=0)
     aircond = models.IntegerField(default=0)
     gas = models.IntegerField(default=0)

     class Meta:
        db_table = 'Equipment'

class Info(models.Model):
     hId = models.OneToOneField(House,primary_key=True,on_delete=models.PROTECT,to_field='hId',auto_created=False)
     price = models.IntegerField(default=0)
     size = models.IntegerField(default=5)
     address = models.CharField(max_length=1000,default="--")
     level = models.IntegerField(default=5)
     room = models.IntegerField(default=1)
     living = models.IntegerField(default=1)
     bath = models.IntegerField(default=1)
     type = models.CharField(max_length=10,default="--")
     class Meta:
        db_table = 'Info'

class Image(models.Model):
     path = models.CharField(max_length=100, primary_key=True,unique=True)
     hId = models.ForeignKey(House,to_field='hId',auto_created=False,on_delete=models.CASCADE)

     class Meta:
        db_table = 'Image'

class Rdetail(models.Model):
     hId = models.OneToOneField(House,primary_key=True,on_delete=models.CASCADE,unique=True,to_field='hId',auto_created=False)
     status = models.IntegerField(default=0)
     parking = models.CharField(max_length=20, default="無")
     pet = models.IntegerField(default=0)
     cook = models.IntegerField(default=0)

     direction = models.CharField(max_length=10, default="--")
     in_level = models.IntegerField(default=1)
     age = models.IntegerField(default=0)
     security = models.CharField(max_length=10, default="--")
     management = models.IntegerField(default=0)

     period = models.CharField(max_length=10, default="--")
     bus = models.IntegerField(default=0)
     train = models.IntegerField(default=0)
     mrt = models.IntegerField(default=0)
     class Meta:
        db_table = 'Rdetail'