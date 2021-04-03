
from cinemanaAPI import *


search_k = str(input('Enter search name: '))

search_result = search(videoTitle=search_k)

for i in search_result:
    print(i)