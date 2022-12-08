from django.http import HttpResponse
from PetModel.models import RightsDescription,UserInfo,PetType,PetInfo ,PetStatus,PetTask,ValuableBook,CommentToDict,UserToPet,FriendRelation,DictPetRelation,PetTypePetRelation,DictCommentRelation

def testdb(request):
  test1 = RightsDescription(rights=10, describe="root priority")
  test1.save()
  return HttpResponse("<p>data add success!</p>")
