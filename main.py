
from numpy.lib.histograms import _histogram_dispatcher
import credential
from plexapi.server import PlexServer
import pandas as pd
from numpy import isnan
from difflib import SequenceMatcher
import time
plex = PlexServer(credential.baseurl,credential.plexrpitoken)

df = pd.read_excel("./TOP-2000-2021.xlsx")

artistlist=[]
titlelist = []

def similar(a, b):
    r=SequenceMatcher(None, a, b).ratio()
    if r>=0.8:
        return True
    else:
        return False

if __name__ == '__main__':
    print("start")

    for i in range(1,df.titel.size):
        counter=0
        resp_okay=False
        found = False
        artist = df.artiest.iloc[i]
        titel = df.titel.iloc[i]
        print("Searching for %s - %s (%i/%i)" %(artist,titel,i,df.titel.size))
        while not resp_okay:
            try:
                resp = plex.search(artist+" "+titel,sectionId=1)
                resp_okay=True
            except Exception as e:
                counter+=1
                print(e)
                resp_okay=False
                time.sleep(1)
                if counter>30:
                    print("adding %s-%s to list"%(artist,titel))
                    artistlist.append(artist)
                    titlelist.append(titel)
                    print("breaking  ")
                    break
        if len(resp)==0:
            print("adding %s-%s to list"%(artist,titel))
            artistlist.append(artist)
            titlelist.append(titel)
        else:
            for j in range(len(resp)):
                if resp[j].TYPE=='track':
                    responsetitle=resp[j].title.lower()
                    responseartist=resp[j].grandparentTitle.lower()
                    if hasattr(resp[j],'originalTitle'):
                        if resp[j].originalTitle is None:
                            originaltitle=""
                        else:
                            originaltitle=resp[j].originalTitle.lower()
                    else:
                        originaltitle = ""
                    
                    if (similar(responseartist,artist.lower()) or similar(originaltitle,artist.lower())) and similar(responsetitle,titel.lower()):
                        found = True
                        print("Found %s - %s" %(responseartist,responsetitle))
                        break
                else:
                    continue
                
            if not found:
                print("adding %s-%s to list"%(artist,titel))
                artistlist.append(artist)
                titlelist.append(titel)

df1 = pd.DataFrame({'artist':artistlist,'track':titlelist})
df1.to_excel("downloadlist.xlsx")