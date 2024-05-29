from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
     username = models.CharField(max_length=100, primary_key=True,unique=True,default="-")
     password= models.CharField(max_length=100, default="--")
     class Meta:
        db_table = 'User'

class Member(models.Model):
     mId = models.IntegerField(primary_key=True, unique=True)
     gender= models.CharField(max_length=50,default="-")
     email = models.CharField(max_length=50,default="-")
     phone = models.CharField(max_length=50,default="-")
     realname = models.CharField(max_length=50, default="-")
     pId = models.CharField(max_length=50,unique=True,null=True)
     username = models.OneToOneField(User,to_field='username',on_delete=models.CASCADE,unique=True,auto_created=False,default="-")

     class Meta:
        db_table = 'Member'

class House(models.Model):
     hId = models.CharField(max_length=100, primary_key=True, unique=True, default="TW")
     status = models.IntegerField(default=0)
     title = models.CharField(max_length=1000)
     region = models.IntegerField(default=00)
     available = models.IntegerField(default=1)
     mId = models.ForeignKey(Member,on_delete=models.CASCADE,to_field='mId',auto_created=False,default="888",unique=False)

     class Meta:
        db_table = 'House'
class Equipment(models.Model):
     hId = models.OneToOneField(House,primary_key=True,on_delete=models.CASCADE,to_field='hId',auto_created=False)
     sofa = models.IntegerField(default=0)
     tv = models.IntegerField(default=0)
     washer = models.IntegerField(default=0)
     wifi = models.IntegerField(default=0)
     bed = models.IntegerField(default=0)
     refrigerator = models.IntegerField(default=0)
     heater = models.IntegerField(default=0)
     channel4 = models.IntegerField(default=0)
     cabinet = models.IntegerField(default=0)
     aircond = models.IntegerField(default=0)
     gas = models.IntegerField(default=0)
     lift = models.IntegerField(default=0)

     class Meta:
        db_table = 'Equipment'

class Info(models.Model):
     hId = models.OneToOneField(House,to_field='hId',primary_key=True,on_delete=models.CASCADE,auto_created=False)
     price = models.IntegerField(default=0)
     size = models.FloatField(default=0)
     address = models.CharField(max_length=1000,default="--")
     level = models.IntegerField(default=5)
     room = models.IntegerField(default=1)
     living = models.IntegerField(default=1)
     bath = models.IntegerField(default=1)
     type = models.CharField(max_length=10,default="--")
     renewdate=models.DateField(null=True,blank=True)
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
     level = models.IntegerField(default=1)
     age = models.FloatField(default=0)
     security = models.CharField(max_length=10, default="--")
     management = models.IntegerField(default=0)

     period = models.CharField(max_length=10, default="--")
     bus = models.IntegerField(default=0)
     train = models.IntegerField(default=0)
     mrt = models.IntegerField(default=0)

     class Meta:
        db_table = 'Rdetail'

class Sdetail(models.Model):
     hId = models.OneToOneField(House,primary_key=True,on_delete=models.CASCADE,unique=True,to_field='hId',auto_created=False)
     status = models.IntegerField(default=0)
     parking = models.CharField(max_length=20, default="無")

     direction = models.CharField(max_length=10, default="--")
     level = models.IntegerField(default=1)
     age = models.FloatField(default=0)
     security = models.CharField(max_length=10, default="--")
     management = models.IntegerField(default=0)
     bus = models.IntegerField(default=0)
     train = models.IntegerField(default=0)
     mrt = models.IntegerField(default=0)
     lift = models.IntegerField(default=0)


     class Meta:
        db_table = 'Sdetail'


class Browse(models.Model):
     browse_seq = models.AutoField(primary_key=True)
     mId = models.ForeignKey(Member,on_delete=models.CASCADE,to_field='mId',auto_created=False,unique=False)
     hId = models.ForeignKey(House, to_field='hId', auto_created=False, on_delete=models.CASCADE,unique=False)

     class Meta:
        db_table = 'Browse'

class Favourite(models.Model):
     favourite_seq = models.AutoField(primary_key=True)
     mId = models.ForeignKey(Member,on_delete=models.CASCADE,to_field='mId',auto_created=False,unique=False)
     hId = models.ForeignKey(House, to_field='hId', auto_created=False, on_delete=models.CASCADE,unique=False)

     class Meta:
        db_table = 'Favourite'

class Review(models.Model):
     review_seq = models.AutoField(primary_key=True)
     text = models.CharField(max_length=1000, default="-")

     mId = models.ForeignKey(Member,on_delete=models.CASCADE,to_field='mId',auto_created=False,unique=False)
     hId = models.ForeignKey(House, to_field='hId', auto_created=False, on_delete=models.CASCADE,unique=False)
     environment = models.IntegerField(default=0)
     attitude = models.IntegerField(default=0)
     facilities = models.IntegerField(default=0)

     class Meta:
        db_table = 'Review'
class Booking(models.Model):
     booking_seq = models.AutoField(primary_key=True)
     customer_id = models.ForeignKey(Member,on_delete=models.CASCADE,to_field='mId',auto_created=False,unique=False)
     hId = models.ForeignKey(House, to_field='hId', auto_created=False, on_delete=models.CASCADE,unique=False)
     date=models.DateField(null=True,blank=True)
     time=models.TimeField(null=True,blank=True)
     situation = models.CharField(default="未確認",null=False,max_length=20)

     class Meta:
        db_table = 'Booking'

class KeyPair(models.Model):
     booking_seq = models.OneToOneField(Booking,primary_key=True,on_delete=models.CASCADE,to_field='booking_seq',auto_created=False,unique=True)
     private_key = models.TextField(max_length=100000000,default="--")
     public_key = models.TextField(max_length=100000000,default="--")
     class Meta:
          db_table = 'KeyPair'