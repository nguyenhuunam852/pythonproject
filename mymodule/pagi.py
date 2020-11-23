
def getpagi(sort_list,n):
  page = float(len(sort_list)/n)
  if(page>int(len(sort_list)/n)):
    page=int(len(sort_list)/n+1)
  else:
    page=int(len(sort_list)/n)
  return page
