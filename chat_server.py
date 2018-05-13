

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        self.ggroup = grp.gGroup(grp.Group)
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        # sonnet
        self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        self.sonnet = pkl.load(self.sonnet_f)
        self.sonnet_f.close()
        # game
        self.mouse_list=[]
        self.hammer_list=[]
        self.score_m = 0
        self.score_h = 0

    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    if self.group.is_member(name) != True:
                        #move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        #add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        #load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name]=pkl.load(open(name+'.idx','rb'))
                            except IOError: #chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps({"action":"login", "status":"ok"}))
                    else: #a client under this name has already logged in
                        mysend(sock, json.dumps({"action":"login", "status":"duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print ('wrong code received')
            else: #client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #read msg code
        msg = myrecv(from_sock)
        #print(len(msg))
        if len(msg) > 0:
            
#==============================================================================
# handle connect request
#==============================================================================
            msg = json.loads(msg)
            print(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action":"connect", "status":"self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps({"action":"connect", "status":"success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"connect", "status":"request", "from":from_name}))
                else:
                    msg = json.dumps({"action":"connect", "status":"no-user"})
                mysend(from_sock, msg)
#==============================================================================
# handle messeage playing: one peer for now. will need multicast later
#==============================================================================
            elif msg["action"] == "invite":
                # people who initiate the invitation send this msg to server
                #  msg = json.dumps({"action":"invite", "target":peer, 'peer_id':peer_id})
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                target_id = msg['peer_id']
                
                if to_name == from_name:
                    msg = json.dumps({"action":"invite", "status":"self"})
                # connect to the peer
                elif self.group.is_member(to_name): # that there is the target people online
                    to_sock = self.logged_name2sock[to_name]
                    self.ggroup.game_connect(from_name, to_name)
                    the_guys = self.ggroup.g_list_me(from_name)
                    msg = json.dumps({"action":"invite", "status":"success", "target_id":target_id})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"invite", "status":"request", \
                                                    "from":from_name,"target_id":target_id}))
                else:
                    msg = json.dumps({"action":"invite", "status":"no-user"})
                mysend(from_sock, msg)
#==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
#==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                #said = msg["from"]+msg["message"]
                said2 = text_proc(msg["message"], from_name)
                self.indices[from_name].add_msg_and_index(said2)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(said2)
                    mysend(to_sock, json.dumps({"action":"exchange", "from":msg["from"], "message":msg["message"]}))
#==============================================================================
# handle messeage playing: one peer for now. will need multicast later
#==============================================================================
            elif msg["action"] == "playing":
                # as normally playing, what is send to server by one client
                # mysend(self.s, json.dumps({"action":"playing", "from":self.me, "target":peer,\
                # "from_id":self.id, "location":chr(event.key)}))

                # print("I am here: playing")
                from_id = msg['from_id']

                scorechange_m = 0
                scorechange_h = 0
                print(from_id)
                if from_id == 'mouse' or from_id == 'bomb':
                    self.mouse_list.append([msg['from'],msg["location"],msg["time"],msg['from_id'], False])
                    hammer = None
                    m_name = msg['from']
                    h_name = msg['target']
                elif from_id == "hammer":
                    print('here')
                    hammer = [msg['from'],msg["location"],msg["time"],msg['from_id'], False]
                    h_name = msg['from']
                    m_name = msg['target']

                mouse_list2=self.mouse_list[:]
                
                print(mouse_list2)
                if hammer is not None:
                    for i in range(len(self.mouse_list)):
                        if mouse_list2[i][1] == hammer[1] and hammer[2] - mouse_list2[i][2] < 15 and mouse_list2[i][4] == False:
                            if mouse_list2[i][3] == "mouse":
                                self.score_h += 10
                                scorechange_h = 10
                            elif mouse_list2[i][3] == "bomb":
                                self.score_m += 10
                                scorechange_m = 10
                            mouse_list2[i][4] = True
                            break
                                    
                to_sock_m = self.logged_name2sock[m_name]     
                to_sock_h = self.logged_name2sock[h_name]
                print("score:", scorechange_m,scorechange_h)
                m_dic = msg
                h_dic = msg
                m_dic["scorechange"] = scorechange_m
                print('m_dict: ',m_dic)
                print('m_name:(should be b)',m_name)
                print(m_dic["scorechange"])
                h_dic["scorechange"] = scorechange_h

                mysend(to_sock_m, json.dumps(m_dic))
                mysend(to_sock_h, json.dumps(h_dic))
#==============================================================================
#                 listing available peers
#==============================================================================
            elif msg["action"] == "list": 
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all(from_name)
                mysend(from_sock, json.dumps({"action":"list", "results":msg}))
#==============================================================================
#             retrieve a sonnet
#==============================================================================
            elif msg["action"] == "poem":
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_sect(poem_indx)
                print('here:\n', poem)
                mysend(from_sock, json.dumps({"action":"poem", "results":poem}))
#==============================================================================
#                 time
#==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps({"action":"time", "results":ctime}))
#==============================================================================
#                 search
#==============================================================================
            elif msg["action"] == "search":
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print('search for ' + from_name + ' for ' + term)
                search_rslt = (self.indices[from_name].search(term)).strip()
                print('server side search: ' + search_rslt)
                mysend(from_sock, json.dumps({"action":"search", "results":search_rslt}))
#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"disconnect"}))
#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif msg["action"] == "g_disconnect":
                if msg["id"] == "mouse" or "bomb":
                    mysend(from_sock, json.dumps({"action":"g_disconnect", "score":self.score_m}))
                else:
                    mysend(from_sock, json.dumps({"action":"g_disconnect", "score":self.score_h}))
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.ggroup.g_list_me(from_name)
                self.group.disconnect(from_name)

                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    if msg["id"] == "mouse" or "bomb":
                        mysend(to_sock, json.dumps({"action": "g_disconnect", "score": self.score_m}))
                    else:
                        mysend(to_sock, json.dumps({"action": "g_disconnect", "score": self.score_h}))
                self.score_m = 0
                self.score_h = 0
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================

        else:
            #client died unexpectedly
            self.logout(from_sock)

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc)
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
               sock, address=self.server.accept()
               self.new_client(sock)

def main():
    server=Server()
    server.run()

main()
