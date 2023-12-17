import credential
from plexapi.server import PlexServer
import pandas as pd
from numpy import arcsin, can_cast, isnan
from difflib import SequenceMatcher
import time




def similar(a, b):
    r=SequenceMatcher(None, a, b).ratio()
    print("%s is %f similar to %s"%(a,r,b))
    if r>=0.4:
        return [True,r]
    else:
        return [False,r]
    

def filterstring(string):
    ignoreterms = ["(Albumversie)",'\ufeff']
    for i in ignoreterms:
        string=string.replace(i,"")
    if "(" in string and ")" in string:
        i1= string.index("(")
        i2= string.index(")")
        if i2>i1:
            string=string[:i1]+string[i2+1:]    
    return string
if __name__ == '__main__':
    print("start")
    plex = PlexServer(credential.baseurl,credential.plextoken)
    df = pd.read_excel("./Top-2000-2023.xlsx")
    artisttest=df['artiest'][804]
    titletest= df['titel'][804]
# df = pd.read_excel("./test.xlsx")

    artistlist=[]
    titlelist = []
    for i in range(1,len(df)):
        print("")
        counter=0
        resp_okay=False
        found = False
        artist = filterstring(df.artiest.iloc[i])
        titel = filterstring(df.titel.iloc[i])
        
        attempt=0
        query = artist+" "+ titel
        while attempt<=1:
            resp_okay=False
            while not resp_okay:
                try:
                    print("Searching for %s (%i/%i)" %(query,i,df.titel.size-1))
                    resp = plex.search(query,sectionId=1)
                    resp_okay=True
                except Exception as e:
                    titel=titel.replace("(","")
                    titel=titel.replace(")","")
                    counter+=1
                    print(e)
                    resp_okay=False
                    time.sleep(1)
                    if counter>10:
                        # print("adding %s-%s to list"%(artist,titel))
                        # artistlist.append(artist)
                        # titlelist.append(titel)
                        print("breaking  ")
                        break
            if len(resp)==0:
                print ("no responses for %s"%query)
                # print("adding %s-%s to list"%(artist,titel))
                # artistlist.append(artist)
                # titlelist.append(titel)
            else:
                print("got %i responses"%len(resp))
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
                        
                        if (similar(responseartist,artist.lower())[0] or similar(originaltitle,artist.lower())[0]) and similar(responsetitle,titel.lower())[0]:
                            found = True
                            print("Found %s -%s- %s" %(responseartist,originaltitle,responsetitle))
                            break
            if not found and attempt<1:
                print("widening search")
                query = titel #widen search once
                searching=False
                attempt+=1
            else:
                break
                
                    
        if not found:
            a="y"#input("%s %s not found. Add to list?(y/n)"%(artist,titel))
            if a=="y":
                print("adding %s-%s to list"%(artist,titel))
                artistlist.append(artist)
                titlelist.append(titel)

    df1 = pd.DataFrame({'artist':artistlist,'track':titlelist})
    df1.to_excel("downloadlist.xlsx")
    f=open("downloadlist.txt",'w',encoding='utf-8')
    for i in range(len(artistlist)):
        try:
            f.write(artistlist[i]+" "+titlelist[i]+"\n")
        except:
            print("error for" + artistlist[i]+" "+titlelist[i])
            continue
    f.close()
    print("finished")