import os
import datetime
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from PetModel.models import RightsDescription,UserInfo,PetType,PetInfo ,PetStatus,PetTask,ValuableBook,CommentToDict,UserToPet,FriendRelation,DictPetRelation,PetTypePetRelation,DictCommentRelation

def adduser(request):
  if request.method == "POST":
    account = request.POST.get("account", 'null')
    password = request.POST.get("password", '123')
    tel = request.POST.get("telephone", '123')
    if account == 'null' or password == '123' or tel == '123': #check if account, password, telephone number exist
      return JsonResponse({"msg": "必须输入用户名，密码和电话号码", "code": 1})
    tmp_account = UserInfo.objects.filter(account=account)
    if len(tmp_account):  #check if account exists in db.
      return JsonResponse({"msg": "该名称已经有人注册", "code": 2})
    name = request.POST.get("name", "null")
    money = 0
    rights = 1
    describe = request.POST.get("describe", 'no describe')
    #image = models.ImageField(verbose_name='UserImage', null=True, upload_to='usrimg/')
    image = request.FILES.get('image', None)
    if image:
        file_info, suffix = os.path.splitext(image.name)
        # 修改照片名称 按需求来进行改写
        image.name = account + suffix
        if suffix.upper() not in ['.JPG', '.JPEG', '.PNG']:
            return JsonResponse({"msg": "照片格式只支持PNG、JPEG、JPG", "code": 3})
        # 判断数据库中该用户是否有上传过照片，如果有，代表我们服务器本地也有这个照片，因为我们model用的是 upload_to 这个，所以 如果照片存在，再次上传同一张照片，系统会自动给你在照片的末尾加上一些字符串来区分并不会替换掉照片，会造成无用的图片越来越多，所以我们要把之间的同一个名字的照片先删除掉，在进行保存
        path = settings.BASE_DIR + '/media/' + str(image)
        if os.path.exists(path):
            os.remove(path)
    userinfo = UserInfo(account=account, password=password, name=name, rights=rights, describe=describe, tel=tel, money=money, image=image)
    userinfo.save()
    return JsonResponse({"msg": "success", "code": 0})

def adddict(request):
  return JsonResponse({"msg":"success"})

def addfriend(request):
  userId1 = request.POST.get("user1", 'null')
  userId2 = request.POST.get("user2", 'null')
  if userId1 == 'null' or userId2 == 'null':
    return JsonResponse({"msg": "请输入用户id", "code": 1})
  tmp_user = UserInfo.objects.filter(Q(account=userId1) | Q(account=userId2))
  if len(tmp_user) != 2:
    return JsonResponse({"msg": "用户id在表中没有查到", "code": 2})

  relation = FriendRelation(userId1=userId1, userId2=userId2)
  relation.save()
  return JsonResponse({"msg":"success", "code":0})

def adddictcomment(request):
  dictId = request.POST.get("dictId", None)
  comment = request.POST.get("comment", None)
  if dictId == None or comment == None:
    return JsonResponse({"msg":"请输入宝典id和评论", "code":1})
  tmpIdList = ValuableBook.objects.filter(dictId=dictId)
  if len(tmpIdList) != 1:
    return JsonResponse({"msg":"数据库中没有宝典记录", "code":2})
  totalAgree = 0
  date = datetime.datetime().now()
  commentList = CommentToDict.objects.filter(dictId=dictId).order_by("-commentId")
  commentId = commentList[0].commentId + 1
  commentObj = CommentToDict(dictId=dictId, commentId=commentId,totalAgree=totalAgree,comment=comment,date=date)
  commentObj.save()
  return JsonResponse({"commentId":commentId, "msg":"success", "code":0})

def addpet(request):
  #petId = 
  #petObj = PetStatus(petId)
  return JsonResponse({"msg":"success"})
'''
class PetStatus(models.Model):
  petId = models.IntegerField(primary_key=True, unique=True)
  userId = models.ForeignKey(to=UserInfo, to_field='account', on_delete=models.CASCADE)
  type = models.ForeignKey(to=PetType, to_field='type', on_delete=models.DO_NOTHING)
  variety = models.ForeignKey(to=PetInfo, to_field='variety', on_delete=models.DO_NOTHING)
  name = models.CharField(max_length=128)
  image = models.ImageField(verbose_name="PetImage", null=True, upload_to='petimage/')
  grow = models.IntegerField()
  hunger = models.IntegerField()
  clean = models.IntegerField()
  active = models.IntegerField()
  healthy = models.IntegerField()
'''
def changepetstatus(request):
  return JsonResponse({"msg":"success"})

def changedictstatus(request):
  return JsonResponse({"msg":"success"})

def changedictcommentstatus(request):
  return JsonResponse({"msg":"success"})

def login(request):
  return JsonResponse({"msg":"success"})

def getdict(request):
  return JsonResponse({"msg":"success"})

def getdictcomment(request):
  return JsonResponse({"msg":"success"})


def getfriend(request):
  return JsonResponse({"msg":"success"})

def getpetstatus(request):
  return JsonResponse({"msg":"success"})

def getuserinfo(request):
  return JsonResponse({"msg":"success"})
'''
    path('adduser/', petdb.adduser),
    path('adddict/', petdb.adddict),
    path('addfriend/', petdb.addfriend),
    path('adddictcomment/', petdb.adddictcomment),
    path('addpet/', petdb.addpet),
    path('changepetstatus/', petdb.changepetstatus),
    path('changedictstatus/', petdb.changedictstatus),
    path('changedictcommentstatus/', petdb.changedictcommentstatus),
    path('login/', petdb.login),
    path('getdict/', petdb.getdict),
    path('getdictcomment/', petdb.getdictcomment),
    path('getfriend/', petdb.getfriend),
    path('getpetstatus/', petdb.getpetstatus),
    path('getuserinfo/', petdb.getuserinfo),
'''
