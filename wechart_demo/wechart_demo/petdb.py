import os
import threading
import datetime
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from PetModel.models import RightsDescription,UserInfo,PetType,PetInfo ,PetStatus,PetTask,ValuableBook,CommentToDict,FriendRelation,DictPetRelation,PetTypePetRelation

comment_lock = threading.Lock()
pet_lock = threading.Lock()
dict_lock = threading.Lock()

def adduser(request):
  if request.method == "POST":
    account = request.POST.get("account", None)
    password = request.POST.get("password", None)
    tel = request.POST.get("telephone", None)
    if account == None or password == None or tel == None: #check if account, password, telephone number exist
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
  return JsonResponse({"msg":"just support post", "code":-1})

def adddict(request):
  if request.method == "POST":
    name = request.POST.get("name", None)
    text = request.POST.get("text", None)
    authorId = request.POST.get("author", None)
    if name == None or text == None or authorId == None:
      return JsonResponse({"msg": "必须输入name,text和authorId", "code": 2})
    userList = UserInfo.objects.filter(account=authorId)
    if len(userList) != 1:
      return JsonResponse({"msg":"数据库中没有用户记录", "code":2})
    likedNum = 0
    commentNum = 0
    forwardNum = 0
    dict_lock.acquire()
    itemObj = ValuableBook.objects.latest()
    dictId = itemObj.dictId + 1
    image = request.FILES.get('image', None)
    if image:
      file_info, suffix = os.path.splitext(image.name)
      image.name = dictId + suffix
      if suffix.upper() not in ['.JPG', '.JPEG', '.PNG']:
          return JsonResponse({"msg": "照片格式只支持PNG、JPEG、JPG", "code": 3})
      path = settings.BASE_DIR + '/media/' + str(image)
      if os.path.exists(path):
        os.remove(path)
    dictObj = ValuableBook(dictId=dictId,likedNum=likedNum,commentNum=commentNum,forwardNum=forwardNum,name=name,text=text,authorId=authorId,image=image)
    dictObj.save()
    dict_lock.release()
    return JsonResponse({"msg":"success"})
  
  return JsonResponse({"msg":"just support post", "code":-1})

def addfriend(request):
  if request.method == "POST":
    userId1 = request.POST.get("user1", None)
    userId2 = request.POST.get("user2", None)
    if userId1 == None or userId2 == None:
      return JsonResponse({"msg": "请输入用户id", "code": 1})
    tmp_user = UserInfo.objects.filter(Q(account=userId1) | Q(account=userId2))
    if len(tmp_user) != 2:
      return JsonResponse({"msg": "用户id在表中没有查到", "code": 2})

    relation = FriendRelation(userId1=userId1, userId2=userId2)
    relation.save()
    return JsonResponse({"msg":"success", "code":0})
  return JsonResponse({"msg":"just support post", "code":-1})

def adddictcomment(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    comment = request.POST.get("comment", None)
    if dictId == None or comment == None:
      return JsonResponse({"msg":"请输入宝典id和评论", "code":1})
    tmpIdList = ValuableBook.objects.filter(dictId=dictId)
    if len(tmpIdList) != 1:
      return JsonResponse({"msg":"数据库中没有宝典记录", "code":2})
    totalAgree = 0
    date = datetime.datetime().now()
    comment_lock.acquire()
    commentList = CommentToDict.objects.filter(dictId=dictId).order_by("-commentId")
    commentId = 1
    if len(commentList) != 0:
      commentId = commentList[0].commentId + 1
    commentObj = CommentToDict(dictId=dictId, commentId=commentId,totalAgree=totalAgree,comment=comment,date=date)
    commentObj.save()
    comment_lock.release()
    return JsonResponse({"commentId":commentId, "msg":"success", "code":0})
  return JsonResponse({"msg":"just support post", "code":-1})

def addpet(request):
  if request.method == "POST":
    userId = request.POST.get("userId", None)
    type = request.POST.get("type", None)
    variety = request.POST.get("variety", None)
    name = request.POST.get("name", None)
    if userId == None or type == None or variety == None or name == None:
      return JsonResponse({"msg":"数据输入不全", "code":1})
    tmpIdList = UserInfo.objects.filter(account=userId)
    if len(tmpIdList) != 1:
      return JsonResponse({"msg":"数据库中没有用户记录", "code":2})
    tmpTypeList = PetInfo.objects.filter(type=type, variety=variety)
    if len(tmpIdList) != 1:
      return JsonResponse({"msg":"数据库中没有宠物记录", "code":2})
    grow = 50
    hunger = 50
    clean = 50
    active = 50
    healthy = 50
    pet_lock.acquire()
    petId = 1
    petList = PetStatus.objects.filter(userId=userId).order_by("-petId")
    if len(petList) != 0:
      petId = petList[0].petId + 1
    image = request.FILES.get('image', None)
    if image:
      file_info, suffix = os.path.splitext(image.name)
      # 修改照片名称 按需求来进行改写
      image.name = userId + "_" + petId + suffix
      if suffix.upper() not in ['.JPG', '.JPEG', '.PNG']:
          pet_lock.release()
          return JsonResponse({"msg": "照片格式只支持PNG、JPEG、JPG", "code": 3})
      # 判断数据库中该用户是否有上传过照片，如果有，代表我们服务器本地也有这个照片，因为我们model用的是 upload_to 这个，所以 如果照片存在，再次上传同一张照片，系统会自动给你在照片的末尾加上一些字符串来区分并不会替换掉照片，会造成无用的图片越来越多，所以我们要把之间的同一个名字的照片先删除掉，在进行保存
      path = settings.BASE_DIR + '/media/' + str(image)
      if os.path.exists(path):
          os.remove(path)
    petObj = PetStatus(petId=petId, userId=userId,type=type,variety=variety,name=name,image=image,grow=grow,hunger=hunger,clean=clean,active=active,healthy=healthy)
    petObj.save()
    pet_lock.release()
    #petId = 
    #petObj = PetStatus(petId)
    return JsonResponse({"petId":petId, "msg":"success", "code":0})
  return JsonResponse({"msg":"just support post", "code":-1})

def changepetstatus(request):
  if request.method == "POST":
    userId = request.POST.get("userId", None)
    petId = request.POST.get("petId", None)
    if userId == None or petId == None:
      return JsonResponse({"msg":"数据输入不全", "code":1})
    petInfo = PetStatus.objects.filter(Q(userId=userId) & Q(petId=petId))
    if len(petInfo) != 1:
      return JsonResponse({"msg":"没有对应的宠物数据", "code":1})
    type = request.POST.get("type", None)
    if type != None:
      petInfo.update(type=type)
    variety = request.POST.get("variety", None)
    if variety != None:
      petInfo.update(variety=variety)
    name = request.POST.get("name", None)
    if name != None:
      petInfo.update(name=name)
    grow = request.POST.get("type", None)
    if grow != None:
      petInfo.update(grow=grow)
    hunger = request.POST.get("variety", None)
    if hunger != None:
      petInfo.update(hunger=hunger)
    clean = request.POST.get("name", None)
    if clean != None:
      petInfo.update(clean=clean)
    active = request.POST.get("active", None)
    if active != None:
      petInfo.update(active=active)
    healthy = request.POST.get("healthy", None)
    if healthy != None:
      petInfo.update(healthy=healthy)
    return JsonResponse({"petInfo":petInfo, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

'''
class ValuableBook(models.Model):
  dictId = models.BigIntegerField(primary_key=True, unique=True)
  likedNum = models.IntegerField()
  commentNum = models.IntegerField()
  forwardNum = models.IntegerField()
  name = models.CharField(max_length=128) #save dict name
  text = models.CharField(max_length=1024) #save dict text
  authorId = models.ForeignKey(to=UserInfo, to_field='account', on_delete=models.DO_NOTHING)
  image = models.ImageField(verbose_name="PetImage", null=True, upload_to='dictimage/')
  #video = models.CharField(max_length=256)  #save video path
  class Meta:
    get_latest_by = 'dictId'
'''

def changedictstatus(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    if dictId == None:
      return JsonResponse({"msg":"数据输入不全,没有dictId", "code":1})
    dictInfo = ValuableBook.objects.filter(dictId=dictId)
    if len(dictInfo) != 1:
      return JsonResponse({"msg":"没有对应的宝典数据", "code":1})
    likedNum = request.POST.get("likedNum", None)
    if likedNum != None:
      dictInfo.update(likedNum=likedNum)
    commentNum = request.POST.get("commentNum", None)
    if commentNum != None:
      dictInfo.update(commentNum=commentNum)
    forwardNum = request.POST.get("forwardNum", None)
    if forwardNum != None:
      dictInfo.update(forwardNum=forwardNum)
    return JsonResponse({"dictInfo":dictInfo, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

def changedictcommentstatus(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    commentId = request.POST.get("commentId", None)
    if dictId == None or commentId == None:
      return JsonResponse({"msg":"数据输入不全", "code":1})
    commentInfo = CommentToDict.objects.filter(Q(dictId=dictId) & Q(commentId=commentId))
    if len(commentInfo) != 1:
      return JsonResponse({"msg":"没有对应的评论数据", "code":1})
    totalAgree = request.POST.get("totalAgree", None)
    if totalAgree != None:
      commentInfo.update(totalAgree=totalAgree)
    return JsonResponse({"commentInfo":commentInfo, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

def login(request):
  if request.method == "POST":
    account = request.POST.get("account", None)
    password = request.POST.get("password", None)
    if account == None or password == None:
      return JsonResponse({"msg":"数据输入不全", "code":1})
    userInfo = UserInfo.objects.filter(Q(account=account) & Q(password=password))
    if len(userInfo) != 1:
      return JsonResponse({"msg":"没有对应的用户数据", "code":1})

    return JsonResponse({"userInfo":userInfo, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

def getdict(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    if dictId != None:
      dictList = ValuableBook.objects.filter(dictId=dictId)
      return JsonResponse({"dictList":dictList, "msg":"success", "code":0})

    dictList = ValuableBook.objects.all()
    return JsonResponse({"dictList":dictList, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

def getdictcomment(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    if dictId != None:
      return JsonResponse({"msg":"必须输入dictId", "code":1})
    commentList = CommentToDict.objects.filter(dictId=dictId)
    return JsonResponse({"commentList":commentList, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

def getfriend(request):
  if request.method == "POST":
    account = request.POST.get("userId", None)
    if account == None:
      return JsonResponse({"msg":"必须输入uerId", "code":1})
    friendObjs = FriendRelation.objects.filter(Q(userId1=account) | Q(userId2=account))
    friendList = []
    for i in range(friendObjs):
      userId1 = friendObjs[i].userId1
      userId2 = friendObjs[i].userId2
      if userId1 == account:
        friendList.append(userId2)
      else:
        friendList.append(userId1)
    return JsonResponse({"friendList":friendList, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

def getpetstatus(request):
  if request.method == "POST":
    userId = request.POST.get("userId", None)
    petId = request.POST.get("petId", None)
    if userId == None or petId == None:
      return JsonResponse({"msg":"数据输入不全", "code":1})
    petInfo = PetStatus.objects.filter(Q(userId=userId) & Q(petId=petId))
    if len(petInfo) != 1:
      return JsonResponse({"msg":"没有对应的宠物数据", "code":1})

    return JsonResponse({"petInfo":petInfo, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

def getuserinfo(request):
  if request.method == "POST":
    account = request.POST.get("account", None)
    password = request.POST.get("password", None)
    if account == None or password == None:
      return JsonResponse({"msg":"数据输入不全", "code":1})
    userInfo = UserInfo.objects.filter(Q(account=account) & Q(password=password))
    if len(userInfo) != 1:
      return JsonResponse({"msg":"没有对应的用户数据", "code":1})

    return JsonResponse({"userInfo":userInfo, "msg":"success", "code":0})

  return JsonResponse({"msg":"just support post", "code":-1})

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
