counter = 15
lickT= 900000
start = 67
startmoment = 89
lickLst = []
rewLst= []
rewT=689

lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])

#print lickLst
#lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])


#New data_sender function: 

def data_sender (lickLst,rewLst): #Modify here since I have more than two entries in each string

    lickStr = 'LickList:' + '-'.join([str(np.round(entry[0],decimals=3))+([str(np.round(entry[1],decimals=3))+([str(np.round(entry[2],decimals=3))+([str(np.round(entry[3],decimals=3))+([str(np.round(entry[4],decimals=3)) for entry in lickLst])
    rewStr = 'rewList:' + '-'.join([str(np.round(entry[0],decimals=3))+([str(np.round(entry[1],decimals=3))+([str(np.round(entry[2],decimals=3))+([str(np.round(entry[3],decimals=3))for entry in rewLst])
    #locStr = 'Location:' + '-'.join([str(np.round(entry[0],decimals=3)) for entry in location])
    #orStr= 'Orientation:' + '-'.join([str(np.round(entry[0],decimals=3)) for entry in orientation])
    sendStr = ','.join([lickStr,rewStr])
    return sendStr

data_sender(lickLst,rewLst)
print sendStr

##        sendProc = billiard.Process(target=send_data,args=(sendStr,))
##        sendProc.start()
##        print 'seeeeeending', (time.time()-start-soundT)
##        #send_data(sendStr)
##        sendT = time.time()
##        lickLst = []; rewLst = []; #No need to empty / update the location/orientation values
##                                   #these will be updated at the start of each trial
##        return lickLst,rewLst,sendT
##
##
##
##        if (time.time()-sendT> 5): #Basically, if 5 seconds have elapsed since the last data_send, then call on that function
##                               #and update the contents of the strings
##        lickLst,rewLst,orientation,location = data_sender(lickLst,rewLst,orientation,location,sendT)    
##  


# Data sending function

pi_IP = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
pi_ID = str(int(pi_IP[-3:])-100) 

def send_data(load):

    headers = {'User-Agent': 'Mozilla/5.0'}
    link = 'http://192.168.0.99:8000/getData/' + pi_ID + '/get_PiData/'

    session = req.Session()
    r1 = session.get(link,headers=headers)

    link1 = 'http://192.168.0.99:8000/getData/' + pi_ID                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       + '/write_PiData/'


    payload = {'piData':load,'csrfmiddlewaretoken':r1.cookies['csrftoken']}
    #cookies = dict(session.cookies)
    session.post(link1,headers=headers,data=payload)
    return None



def data_sender (lickLst,rewLst,orientation, location, sendT): #Modify here since I have more than two entries in each string

        lickStr = 'LickList:' + '-'.join([str(np.round(entry[0],decimals=3))+ ' ' + str(np.round(entry[1],decimals=3))+ ' ' + str(np.round(entry[2],decimals=3))+ ' ' + entry[3] + ' ' + entry[4] for entry in lickLst])
        rewStr = 'rewList:' + '-'.join([str(np.round(entry[0],decimals=3))+ ' ' + str(np.round(entry[1],decimals=3))+ ' ' + str(np.round(entry[2],decimals=3))+ ' ' + entry[3] for entry in rewLst])
        locStr = 'Location:' + '-'.join([str(np.round(location,decimals=3))])
        orStr= 'Orientation:' + '-'.join([str(np.round(orientation,decimals=3))])
        sendStr = ', '.join([rewStr,lickStr,locStr,orStr])
                    
        sendProc = billiard.Process(target=send_data,args=(sendStr,))
        sendProc.start()
        print 'seeeeeending', (time.time()-start-soundT)
        #send_data(sendStr)
        sendT = time.time()
        lickLst = []; rewLst = []; #No need to empty / update the location/orientation values
                                   #these will be updated at the start of each trial
        return lickLst,rewLst,sendT
