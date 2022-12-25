import os
import threading
import datetime, time
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from PetModel.models import *
from django.core import serializers
#from PetModel.models import UserInfo,PetInfo,PetStatus,PetTask,ValuableBook,CommentToDict,FriendRelation,DictPetRelation,PetTypePetRelation

comment_lock = threading.Lock()
pet_lock = threading.Lock()
dict_lock = threading.Lock()
petinfo_lock = threading.Lock()

def adduser(request):
  if request.method == "POST":
    account = request.POST.get("account", None)
    password = request.POST.get("password", None)
    tel = request.POST.get("telephone", None)
    if account == None or password == None or tel == None: #check if account, password, telephone number exist
      return JsonResponse(data={"msg": "必须输入用户名，密码和电话号码", "code": 1},json_dumps_params={"ensure_ascii":False})
    tmp_account = UserInfo.objects.filter(account=account)
    if len(tmp_account):  #check if account exists in db.
      return JsonResponse(data={"msg": "该名称已经有人注册", "code": 2},json_dumps_params={"ensure_ascii":False})
    name = request.POST.get("name", "null")
    money = 0
    rights = 1
    describe = request.POST.get("describe", 'no describe')
    #image = models.ImageField(verbose_name='UserImage', null=True, upload_to='usrimg/')
    image = request.FILES.get('image', None)
    print(image)
    if image:
        file_info, suffix = os.path.splitext(image.name)
        # 修改照片名称 按需求来进行改写
        image.name = account + suffix
        if suffix.upper() not in ['.JPG', '.JPEG', '.PNG']:
            return JsonResponse(data={"msg": "照片格式只支持PNG、JPEG、JPG", "code": 3},json_dumps_params={"ensure_ascii":False})
        # 判断数据库中该用户是否有上传过照片，如果有，代表我们服务器本地也有这个照片，因为我们model用的是 upload_to 这个，所以 如果照片存在，再次上传同一张照片，系统会自动给你在照片的末尾加上一些字符串来区分并不会替换掉照片，会造成无用的图片越来越多，所以我们要把之间的同一个名字的照片先删除掉，在进行保存
        path = os.path.join(settings.BASE_DIR,'/media/',str(image))
        #path = settings.BASE_DIR + '/media/' + str(image)
        if os.path.exists(path):
            os.remove(path)
    userinfo = UserInfo(account=account, password=password, name=name, rights=rights, describe=describe, tel=tel, money=money, image=image)
    userinfo.save()
    
    return JsonResponse(data={"msg": "success", "code": 0},json_dumps_params={"ensure_ascii":False})
  return JsonResponse(data={"msg":"just support post", "code":-1},json_dumps_params={"ensure_ascii":False})

def adddict(request):
  if request.method == "POST":
    name = request.POST.get("name", None)
    text = request.POST.get("text", None)
    authorId = request.POST.get("author", None)
    if name == None or text == None or authorId == None:
      return JsonResponse({"msg": "必须输入name,text和authorId", "code": 2}, json_dumps_params={"ensure_ascii":False})
    print('name:' + name + ', text:' + text + ', authorId:' + authorId)
    userList = UserInfo.objects.filter(account=authorId)
    if len(userList) != 1:
      return JsonResponse({"msg":"数据库中没有用户记录", "code":2}, json_dumps_params={"ensure_ascii":False})
    likedNum = 0
    commentNum = 0
    forwardNum = 0
    dict_lock.acquire()
    dictId = 0
    try:
      dictId = int(ValuableBook.objects.latest().dictId) + 1
    except ValuableBook.DoesNotExist:
      dictId = 1
    image = request.FILES.get('image', None)
    if image:
      file_info, suffix = os.path.splitext(image.name)
      image.name = str(dictId) + suffix
      if suffix.upper() not in ['.JPG', '.JPEG', '.PNG']:
          dict_lock.release()
          return JsonResponse({"msg": "照片格式只支持PNG、JPEG、JPG", "code": 3})
      #path = settings.BASE_DIR + '/media/' + str(image)
      path = os.path.join(settings.BASE_DIR,'/media/',str(image))
      if os.path.exists(path):
        os.remove(path)
    dictObj = ValuableBook(dictId=dictId,likedNum=likedNum,commentNum=commentNum,forwardNum=forwardNum,name=name,text=text,authorId=UserInfo.objects.get(account=authorId),image=image)
    dictObj.save()
    dict_lock.release()
    return JsonResponse({"msg":"success", "dictId": dictId}, json_dumps_params={"ensure_ascii":False})
  
  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def addfriend(request):
  if request.method == "POST":
    userId1 = request.POST.get("user1", None)
    userId2 = request.POST.get("user2", None)
    if userId1 == None or userId2 == None:
      return JsonResponse({"msg": "请输入用户id", "code": 1}, json_dumps_params={"ensure_ascii":False})
    tmp_user = UserInfo.objects.filter(Q(account=userId1) | Q(account=userId2))
    if len(tmp_user) != 2:
      return JsonResponse({"msg": "用户id在表中没有查到", "code": 2}, json_dumps_params={"ensure_ascii":False})

    relation = FriendRelation(userId1=UserInfo.objects.get(account=userId1), userId2=UserInfo.objects.get(account=userId2))
    relation.save()
    return JsonResponse({"msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})
  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def adddictcomment(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    comment = request.POST.get("comment", None)
    if dictId == None or comment == None:
      return JsonResponse({"msg":"请输入宝典id和评论", "code":1}, json_dumps_params={"ensure_ascii":False})
    tmpIdList = ValuableBook.objects.filter(dictId=dictId)
    if len(tmpIdList) != 1:
      return JsonResponse({"msg":"数据库中没有宝典记录", "code":2}, json_dumps_params={"ensure_ascii":False})
    totalAgree = 0
    date = datetime.datetime.now()
    #now = time.strftime("%Y-%m-%d %H:%M:%S")
    #now = datetime.datetime.now()
    #return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})
    comment_lock.acquire()
    commentList = CommentToDict.objects.filter(dictId=dictId).order_by("-commentId")
    commentId = 1
    if len(commentList) != 0:
      commentId = commentList[0].commentId + 1
    commentObj = CommentToDict(dictId=ValuableBook.objects.get(dictId=dictId), commentId=commentId,totalAgree=totalAgree,comment=comment,date=date)
    commentObj.save()
    comment_lock.release()
    return JsonResponse({"commentId":commentId, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})
  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def addpet(request):
  if request.method == "POST":
    userId = request.POST.get("userId", None)
    type = request.POST.get("type", None)
    variety = request.POST.get("variety", None)
    name = request.POST.get("name", None)
    if userId == None or type == None or variety == None or name == None:
      return JsonResponse({"msg":"数据输入不全", "code":1}, json_dumps_params={"ensure_ascii":False})
    tmpIdList = UserInfo.objects.filter(account=userId)
    if len(tmpIdList) != 1:
      return JsonResponse({"msg":"数据库中没有用户记录", "code":2}, json_dumps_params={"ensure_ascii":False})
    tmpTypeList = PetInfo.objects.filter(type=type, variety=variety)
    if len(tmpTypeList) != 1:
      return JsonResponse({"msg":"数据库中没有宠物记录", "code":2}, json_dumps_params={"ensure_ascii":False})
    grow = 50
    hunger = 50
    clean = 50
    active = 50
    healthy = 50
    pet_lock.acquire()
    petList = PetStatus.objects.filter(userId=UserInfo.objects.get(account=userId))
    if len(petList) == 0:
      petId = 1
    else:
      petList = sorted(petList, key=lambda item: item.petId, reverse=True)
      petId = petList[0].petId + 1
    image = request.FILES.get('image', None)
    if image:
      file_info, suffix = os.path.splitext(image.name)
      # 修改照片名称 按需求来进行改写
      image.name = userId + "_" + str(petId) + suffix
      if suffix.upper() not in ['.JPG', '.JPEG', '.PNG']:
          pet_lock.release()
          return JsonResponse({"msg": "照片格式只支持PNG、JPEG、JPG", "code": 3}, json_dumps_params={"ensure_ascii":False})
      # 判断数据库中该用户是否有上传过照片，如果有，代表我们服务器本地也有这个照片，因为我们model用的是 upload_to 这个，所以 如果照片存在，再次上传同一张照片，系统会自动给你在照片的末尾加上一些字符串来区分并不会替换掉照片，会造成无用的图片越来越多，所以我们要把之间的同一个名字的照片先删除掉，在进行保存
      #path = settings.BASE_DIR + '/media/' + str(image)
      path = os.path.join(settings.BASE_DIR,'/media/',str(image))
      if os.path.exists(path):
          os.remove(path)
    petObj = PetStatus(petId=petId, userId=UserInfo.objects.get(account=userId),petType=type,petVariety=variety,name=name,image=image,grow=grow,hunger=hunger,clean=clean,active=active,healthy=healthy)
    petObj.save()
    pet_lock.release()
    return JsonResponse({"user":userId, "petId":petId, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})
  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def changepetstatus(request):
  if request.method == "POST":
    userId = request.POST.get("userId", None)
    petId = request.POST.get("petId", None)
    if userId == None or petId == None:
      print("userId:"+userId+", petId:"+str(petId))
      return JsonResponse({"msg":"数据输入不全", "code":1}, json_dumps_params={"ensure_ascii":False})
    tmpIdList = UserInfo.objects.filter(account=userId)
    if len(tmpIdList) != 1:
      return JsonResponse({"msg":"数据库中没有用户记录", "code":2}, json_dumps_params={"ensure_ascii":False})
    petInfo = PetStatus.objects.filter(Q(userId=UserInfo.objects.get(account=userId)) & Q(petId=petId))
    if len(petInfo) != 1:
      return JsonResponse({"msg":"没有对应的宠物数据", "code":1}, json_dumps_params={"ensure_ascii":False})
    petInfo = PetStatus.objects.get(Q(userId=UserInfo.objects.get(account=userId)) & Q(petId=petId))
    try:
      name = request.POST.get("name", None)
      if name != None:
        petInfo.name=name
      grow = request.POST.get("grow", None)
      if grow != None:
        petInfo.grow=grow
      hunger = request.POST.get("hunger", None)
      if hunger != None:
        petInfo.hunger=hunger
      clean = request.POST.get("clean", None)
      if clean != None:
        petInfo.clean=clean
      active = request.POST.get("active", None)
      if active != None:
        petInfo.active=active
      healthy = request.POST.get("healthy", None)
      if healthy != None:
        petInfo.healthy=healthy
      image = request.FILES.get('image', None)
      if image:
        file_info, suffix = os.path.splitext(image.name)
        # 修改照片名称 按需求来进行改写
        print("userId:"+str(userId)+", petId:"+str(petId)+", suffix:"+suffix)
        image.name = userId + "_" + str(petId) + suffix
        print("image.name:"+image.name)
        if suffix.upper() not in ['.JPG', '.JPEG', '.PNG']:
            return JsonResponse({"msg": "照片格式只支持PNG、JPEG、JPG", "code": 3}, json_dumps_params={"ensure_ascii":False})
        # 判断数据库中该用户是否有上传过照片，如果有，代表我们服务器本地也有这个照片，因为我们model用的是 upload_to 这个，所以 如果照片存在，再次上传同一张照片，系统会自动给你在照片的末尾加上一些字符串来区分并不会替换掉照片，会造成无用的图片越来越多，所以我们要把之间的同一个名字的照片先删除掉，在进行保存
        #path = settings.BASE_DIR + '/media/' + str(image)
        path = os.path.join(settings.BASE_DIR,'/media/',str(image))
        print("path:"+path)
        if os.path.exists(path):
            os.remove(path)
        petInfo.image=image
      petInfo.save()
    except Exception as res:
      return JsonResponse({"msg": str(res), "code":3}, json_dumps_params={"ensure_ascii":False})
    petInfo = PetStatus.objects.filter(Q(userId=UserInfo.objects.get(account=userId)) & Q(petId=petId))
    json_data = serializers.serialize('json', petInfo)
    return JsonResponse({"petInfo":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

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
      return JsonResponse({"msg":"数据输入不全,没有dictId", "code":1}, json_dumps_params={"ensure_ascii":False})
    dictInfo = ValuableBook.objects.filter(dictId=dictId)
    if len(dictInfo) != 1:
      return JsonResponse({"msg":"没有对应的宝典数据", "code":1}, json_dumps_params={"ensure_ascii":False})
    dictInfo = ValuableBook.objects.get(dictId=dictId)
    try:
      likedNum = request.POST.get("likedNum", None)
      if likedNum != None:
        dictInfo.likedNum=likedNum
      commentNum = request.POST.get("commentNum", None)
      if commentNum != None:
        dictInfo.commentNum=commentNum
      forwardNum = request.POST.get("forwardNum", None)
      if forwardNum != None:
        dictInfo.forwardNum=forwardNum
      dictInfo.save()
    except Exception as res:
      return JsonResponse({"msg": str(res), "code":3}, json_dumps_params={"ensure_ascii":False})
    dictInfo = ValuableBook.objects.filter(dictId=dictId)
    json_data = serializers.serialize('json', dictInfo)
    return JsonResponse({"dictInfo":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def changedictcommentstatus(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    commentId = request.POST.get("commentId", None)
    if dictId == None or commentId == None:
      return JsonResponse({"msg":"数据输入不全", "code":1}, json_dumps_params={"ensure_ascii":False})
    dictInfo = ValuableBook.objects.filter(dictId=dictId)
    if len(dictInfo) != 1:
      return JsonResponse({"msg":"没有对应的宝典数据", "code":1}, json_dumps_params={"ensure_ascii":False})
    commentInfo = CommentToDict.objects.filter(Q(dictId=ValuableBook.objects.get(dictId=dictId)) & Q(commentId=commentId))
    if len(commentInfo) != 1:
      return JsonResponse({"msg":"没有对应的评论数据", "code":1})
    totalAgree = request.POST.get("totalAgree", None)
    commentInfo = CommentToDict.objects.get(Q(dictId=ValuableBook.objects.get(dictId=dictId)) & Q(commentId=commentId))
    try:
      if totalAgree != None:
        commentInfo.totalAgree=totalAgree
        commentInfo.save()
      commentInfo = CommentToDict.objects.filter(Q(dictId=ValuableBook.objects.get(dictId=dictId)) & Q(commentId=commentId))
      json_data = serializers.serialize('json', commentInfo)
      return JsonResponse({"commentInfo":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})
    except Exception as res:
      return JsonResponse({"msg": str(res), "code":3}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def login(request):
  if request.method == "POST":
    account = request.POST.get("account", None)
    password = request.POST.get("password", None)
    if account == None or password == None:
      return JsonResponse({"msg":"数据输入不全", "code":1}, json_dumps_params={"ensure_ascii":False})
    userInfo = UserInfo.objects.filter(Q(account=account) & Q(password=password))
    if len(userInfo) != 1:
      return JsonResponse({"msg":"没有对应的用户数据", "code":1}, json_dumps_params={"ensure_ascii":False})
    json_data = serializers.serialize('json', userInfo)
    return JsonResponse({"userInfo":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def getdict(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    if dictId != None:
      dictList = ValuableBook.objects.filter(dictId=dictId)
      json_data = serializers.serialize('json', dictList)
      return JsonResponse({"dictList":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

    dictList = ValuableBook.objects.all()
    json_data = serializers.serialize('json', dictList)
    return JsonResponse({"dictList":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def getdictcomment(request):
  if request.method == "POST":
    dictId = request.POST.get("dictId", None)
    if dictId == None:
      return JsonResponse({"msg":"必须输入dictId", "code":1}, json_dumps_params={"ensure_ascii":False})
    commentList = CommentToDict.objects.filter(dictId=dictId)
    json_data = serializers.serialize('json', commentList)
    return JsonResponse({"commentList":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def getfriend(request):
  if request.method == "POST":
    account = request.POST.get("userId", None)
    if account == None:
      return JsonResponse({"msg":"必须输入uerId", "code":1}, json_dumps_params={"ensure_ascii":False})
    friendObjs = UserInfo.objects.filter(account=account)
    if len(friendObjs) != 1:
      return JsonResponse({"msg":"没有对应的用户数据", "code":1}, json_dumps_params={"ensure_ascii":False})
    friendObjs = FriendRelation.objects.filter(Q(userId1=UserInfo.objects.get(account=account)) | Q(userId2=UserInfo.objects.get(account=account)))
    friendList = []
  
    for one in friendObjs:
      userId1 = one.userId1
      userId2 = one.userId2
      
      if userId1 == account:
        friendList.append(str(userId2.account))
      else:
        friendList.append(str(userId1.account))
      
    return JsonResponse({"friendList":friendList, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def getpetstatus(request):
  if request.method == "POST":
    userId = request.POST.get("userId", None)
    petId = request.POST.get("petId", None)
    if userId == None or petId == None:
      return JsonResponse({"msg":"数据输入不全", "code":1}, json_dumps_params={"ensure_ascii":False})
    petInfo = PetStatus.objects.filter(Q(userId=userId) & Q(petId=petId))
    if len(petInfo) != 1:
      return JsonResponse({"msg":"没有对应的宠物数据", "code":1}, json_dumps_params={"ensure_ascii":False})
    json_data = serializers.serialize('json', petInfo)
    return JsonResponse({"petInfo":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def getuserinfo(request):
  if request.method == "POST":
    account = request.POST.get("account", None)
    #password = request.POST.get("password", None)
    if account == None:
      return JsonResponse({"msg":"数据输入不全", "code":1}, json_dumps_params={"ensure_ascii":False})
    userInfo = UserInfo.objects.filter(account=account)
    if len(userInfo) != 1:
      return JsonResponse({"msg":"没有对应的用户数据", "code":1}, json_dumps_params={"ensure_ascii":False})
    json_data = serializers.serialize('json', userInfo)
    return JsonResponse({"userInfo":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def addpetinfo(request):
  if request.method == "POST":
    type = request.POST.get("type", None)
    variety = request.POST.get("variety", None)
    typeName = request.POST.get("typename", None)
    varietyName = request.POST.get("varietyname", None)
    if type == None or variety == None or typeName == None or varietyName == None:
      return JsonResponse({"msg":"数据输入不全", "code":1}, json_dumps_params={"ensure_ascii":False})
    petinfo_lock.acquire()
    petInfo = PetInfo.objects.filter(Q(type=type) & Q(variety=variety))
    if len(petInfo) > 0:
      petinfo_lock.release()
      return JsonResponse(data={"msg": "该宠物类型已经有人注册", "code": 2},json_dumps_params={"ensure_ascii":False})
    image = request.FILES.get('image', None)
    if image:
      file_info, suffix = os.path.splitext(image.name)
      # 修改照片名称 按需求来进行改写
      image.name = type + "_" + variety + suffix
      if suffix.upper() not in ['.JPG', '.JPEG', '.PNG']:
          petinfo_lock.release()
          return JsonResponse({"msg": "照片格式只支持PNG、JPEG、JPG", "code": 3})
      # 判断数据库中该用户是否有上传过照片，如果有，代表我们服务器本地也有这个照片，因为我们model用的是 upload_to 这个，所以 如果照片存在，再次上传同一张照片，系统会自动给你在照片的末尾加上一些字符串来区分并不会替换掉照片，会造成无用的图片越来越多，所以我们要把之间的同一个名字的照片先删除掉，在进行保存
      #path = settings.BASE_DIR + '/media/' + str(image)
      path = os.path.join(settings.BASE_DIR,'/media/',str(image))
      if os.path.exists(path):
          os.remove(path)
    petInfoObj = PetInfo(type=type, variety=variety,typeName=typeName,varietyName=varietyName,image1=image)
    petInfoObj.save()
    petinfo_lock.release()
    return JsonResponse({"msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})

  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})

def getpetinfo(request):
  if request.method == "POST":
    infoList = request.POST.get("infotype", None)
    if infoList != None and infoList == "all":
      petInfoList = PetInfo.objects.all()
      json_data = serializers.serialize('json', petInfoList)
      return JsonResponse({"petInfo":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})
    type = request.POST.get("type", None)
    variety = request.POST.get("variety", None)
    if type == None or variety == None:
      return JsonResponse({"msg":"数据输入不全", "code":1}, json_dumps_params={"ensure_ascii":False})
    petInfo = PetInfo.objects.filter(Q(type=type) & Q(variety=variety))
    if len(petInfo) != 1:
      return JsonResponse({"msg":"没有对应的宠物数据", "code":1}, json_dumps_params={"ensure_ascii":False})
    json_data = serializers.serialize('json', petInfo)
    return JsonResponse({"petInfo":json_data, "msg":"success", "code":0}, json_dumps_params={"ensure_ascii":False})
  return JsonResponse({"msg":"just support post", "code":-1}, json_dumps_params={"ensure_ascii":False})
'''
    path('admin/', admin.site.urls),
    path('hello/', views.hello),
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
    path('addpetinfo/', petdb.addpetinfo),
    path('getpetinfo/', petdb.getpetinfo),
'''
