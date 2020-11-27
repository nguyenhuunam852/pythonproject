import json
from manager.models import Library_Words
from manager.models import Library_Words_Web
from urlpage.models import Urlspage
def checkWord(word,website):
    if(Library_Words.objects.filter(name=word.upper()).exists()):
         print('xoa '+word)
         word = Library_Words.objects.get(name=word)
         page = Urlspage.objects.get(id=website)
         word_web = Library_Words_Web.objects.create(id_libword=word,id_web=page)
         return 0
    return 1
  

        

