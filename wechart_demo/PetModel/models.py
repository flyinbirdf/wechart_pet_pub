from django.db import models

# Create your models here.
'''
class RightsDescription(models.Model):
  rights = models.IntegerField(primary_key=True)
  describe = models.CharField(max_length=128)
'''
class UserInfo(models.Model):
  account = models.CharField(max_length=128, primary_key=True)
  name = models.CharField(max_length=128)
  password = models.CharField(max_length=128)
  tel = models.CharField(max_length=16)
  money = models.BigIntegerField()
  #rights = models.ForeignKey(to=RightsDescription, to_field="rights", on_delete=models.DO_NOTHING)
  rights = models.IntegerField()
  describe = models.CharField(max_length=256)
  image = models.ImageField(verbose_name='UserImage', null=True, upload_to='usrimg/')

class PetInfo(models.Model):
  #name = models.CharField(max_length=128)  #name
  #type = models.ForeignKey(to=PetType, to_field='type', on_delete=models.CASCADE)  #type
  type = models.IntegerField()
  typeName = models.CharField(max_length=128)
  variety = models.IntegerField()
  varietyName = models.CharField(max_length=128)
  image1 = models.ImageField(verbose_name='PetTypeImage', null=True, upload_to='pettypeimg/')
  class Meta:
    #constraints = [models.UniqueConstraint(fields=['type','variety'], name='pet')]
    unique_together=("type", "variety")

class PetStatus(models.Model):
  petId = models.IntegerField(primary_key=True, unique=True)
  userId = models.ForeignKey(to=UserInfo, to_field='account', on_delete=models.CASCADE)
  petType = models.IntegerField()
  petVariety = models.IntegerField()
  #petType = models.ForeignKey(to=PetInfo, to_field='type', related_name='petType', on_delete=models.CASCADE)
  #petVariety = models.ForeignKey(to=PetInfo, to_field='variety', related_name='petVariety',on_delete=models.CASCADE)
  name = models.CharField(max_length=128)
  image = models.ImageField(verbose_name="PetImage", null=True, upload_to='petimage/')
  grow = models.IntegerField()
  hunger = models.IntegerField()
  clean = models.IntegerField()
  active = models.IntegerField()
  healthy = models.IntegerField()
  class Meta:
    unique_together=("userId", "petId")

class PetTask(models.Model):
  taskId = models.BigIntegerField(primary_key=True, unique=True)
  text = models.CharField(max_length=128)
  petId = models.ForeignKey(to=PetStatus,to_field='petId', on_delete=models.CASCADE)
  isFinish = models.BooleanField()
  growPet = models.IntegerField()
  growType = models.IntegerField()
  growValue = models.IntegerField()

class ValuableBook(models.Model):
  dictId = models.BigIntegerField(primary_key=True, unique=True)
  likedNum = models.IntegerField()
  commentNum = models.IntegerField()
  forwardNum = models.IntegerField()
  name = models.CharField(max_length=128) #save dict name
  text = models.CharField(max_length=1024) #save dict text
  authorId = models.ForeignKey(to=UserInfo, to_field='account', on_delete=models.CASCADE)
  image = models.ImageField(verbose_name="PetImage", null=True, upload_to='dictimage/')
  #video = models.CharField(max_length=256)  #save video path
  class Meta:
    get_latest_by = 'dictId'

class CommentToDict(models.Model):
  dictId = models.ForeignKey(to=ValuableBook,to_field='dictId', on_delete=models.CASCADE)
  commentId = models.IntegerField()
  totalAgree = models.IntegerField()
  comment = models.CharField(max_length=1024)
  date = models.DateTimeField()
  class Meta:
    unique_together=("dictId", "commentId")

class FriendRelation(models.Model):
  userId1 = models.ForeignKey(to=UserInfo, to_field='account',related_name='userId1', on_delete=models.CASCADE)
  userId2 = models.ForeignKey(to=UserInfo, to_field='account',related_name='userId2', on_delete=models.CASCADE)
  class Meta:
    unique_together=("userId1", "userId2")

class DictPetRelation(models.Model):
  #petType = models.ForeignKey(to=PetInfo, to_field='type', related_name='petType', on_delete=models.CASCADE)
  #petVariety = models.ForeignKey(to=PetInfo, to_field='variety', related_name='petVariety', on_delete=models.CASCADE)
  petType = models.IntegerField()
  petVariety = models.IntegerField()
  valuableBook = models.ForeignKey(to=ValuableBook,to_field='dictId', on_delete=models.CASCADE)
  class Meta:
    unique_together=("petType","petVariety","valuableBook") 

class PetTypePetRelation(models.Model):
  #petType = models.ForeignKey(to=PetInfo, to_field='type', related_name='petType', on_delete=models.CASCADE)
  #petVariety = models.ForeignKey(to=PetInfo, to_field='variety', related_name='petVariety', on_delete=models.CASCADE)
  petType = models.IntegerField()
  petVariety = models.IntegerField()
  petId = models.ForeignKey(to=PetStatus,to_field='petId', on_delete=models.CASCADE)
  class Meta:
    unique_together=("petType","petVariety","petId")
