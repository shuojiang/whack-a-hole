
from chat_utils import *
import json

import pygame, sys
from pygame.locals import *
from sys import exit

import time

# position dictionar
mouse_d = {'q':(0, 250),\
     'w':(123, 250),\
     'e':(245, 250),\
     'r':(361, 250),\
     't':(483, 250),\
     'y':(604, 250),\
     'u':(721, 250),\
     'i':(842, 250),\
     'o':(965, 250),\
     'p':(1080, 250),\
     'a':(28, 367),\
     's':(151, 367),\
     'd':(273, 367),\
     'f':(389, 367),\
     'g':(511, 367),\
     'h':(632, 367),\
     'j':(749, 367),\
     'k':(870, 367),\
     'l':(993, 367),\
     'z':(92, 484),\
     'x':(214, 484),\
     'c':(336, 484),\
     'v':(452, 484),\
     'b':(574, 484),\
     'n':(695, 484),\
     'm':(812, 484)}
bomb_d = {}
for i in mouse_d.keys():
    bomb_d[i] = (mouse_d[i][0], mouse_d[i][1]-2)
hammer_d = {}
for i in mouse_d.keys():
    hammer_d[i] = (mouse_d[i][0], mouse_d[i][1]-4)

# file name
background_f = "hole.jpg"
mouse_f = 'mouse.jpg'
hammer_f = 'hammer.jpg'
bomb_f = 'bomb.jpg'
titlem_f = 'title mouse.png'
titleh_f = 'title hammer.png'
class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.g_peer = ''

        self.background = None
        self.mouse = None 
        self.hammer = None
        self.bomb = None
        self.title_mouse = None
        self.title_hammer = None
        self.screen = None

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)
    def invite(self, peer, peer_id):
        msg = json.dumps({"action":"invite", "target":peer, 'peer_id':peer_id})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are ready to start the game with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot play with yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False) 

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''
        
    def g_disconnect(self):
        msg = json.dumps({"action":"gdisconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are nolonger playing with ' + self.peer + '\n'
        self.g_peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(peer_msg) > 0:
                # print(peer_msg)
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

                elif peer_msg["action"] == "invite":
                    # you receive msg as below from server if someone sends you an invitation
                    # msg = json.dumps({"action":"invite", "status":"success", "target_id":target_id})
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer + '\n'
                    self.out_msg += "Let's start our game \n\n"
                    self.out_msg += 'Rule: There are two players in this whack-a-mole game, \
one player represents the “mouse” side, you may choose to jump out of the hole as a mouse, \
or you may choose to jump out as a bomb to trick your peer; \
the other player represents the hammer side, you will be needed avoid the bomb and hit the mouse.!!!\
Caution: you can determine the location of which hole to appear with the 26-character keyboard\
And that you can swtich between bomb and mouse by pressing "SPACE"\
This game is supposed to be infinite:) Unless you find it not it not interesting to play anymore or think that you’ll lose. \
Click the "X" in your window to end the game. Happy playing<3\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_PLAYING
                    self.id = peer_msg["target_id"]
                    pygame.init()
                    self.screen = pygame.display.set_mode((1200, 630))
                    self.background = pygame.image.load(background_f).convert_alpha()
                    self.mouse = pygame.image.load(mouse_f).convert_alpha()
                    self.hammer = pygame.image.load(hammer_f).convert_alpha()
                    self.bomb = pygame.image.load(bomb_f).convert_alpha()
                    self.title_mouse = pygame.image.load(titlem_f).convert_alpha()
                    self.title_hammer = pygame.image.load(titleh_f).convert_alpha()
                    pygame.display.set_caption("whack-a-mole")

                elif peer_msg["action"] == "g_disconnect":
                    print("your score is: ", peer_msg["score"])

            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                                       
                elif my_msg[0] == 'i':
                    my_id = my_msg[1]
                    try:
                        if int(my_id) == 1:
                            self.id = 'mouse'
                            peer_id = 'hammer'
                        elif int(my_id) == 2:
                            self.id = 'hammer'
                            peer_id = 'mouse'
                        peer = my_msg[2:]
                        peer = peer.strip()
                        if self.invite(peer, peer_id) == True:
                            self.state = S_PLAYING
                            self.out_msg += 'You can play whack-a-mole with ' + peer + " now. Let's start\n\n"
                            self.out_msg += 'Rule: There are two players in this whack-a-mole game, \
one player represents the “mouse” side, you may choose to jump out of the hole as a mouse, \
or you may choose to jump out as a bomb to trick your peer; \
the other player represents the hammer side, you will be needed avoid the bomb and hit the mouse.!!!\
Caution: you can determine the location of which hole to appear with the 26-character keyboard\
And that you can swtich between bomb and mouse by pressing "SPACE"\
This game is supposed to be infinite:) Unless you find it not it not interesting to play anymore or think that you’ll lose. \
Click the "X" in your window to end the game. Happy playing<3\n'
                            self.out_msg += '-----------------------------------\n'
                            pygame.init()
                            self.screen=pygame.display.set_mode((1200,630))  

                            self.background = pygame.image.load(background_f).convert_alpha()
                            self.mouse = pygame.image.load(mouse_f).convert_alpha() 
                            self.hammer = pygame.image.load(hammer_f).convert_alpha()
                            self.bomb = pygame.image.load(bomb_f).convert_alpha() 
                            self.title_mouse = pygame.image.load(titlem_f).convert_alpha()
                            self.title_hammer = pygame.image.load(titleh_f).convert_alpha()
                            pygame.display.set_caption("whack-a-mole")
                        else:
                            self.out_msg += 'Request unsuccessful\n'
                        
                    except:
                        self.out_msg += menu
                                        
                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    self.out_msg += menu
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                else:
                    self.out_msg += peer_msg["from"] + peer_msg["message"]          

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# Start playing, 'fine' for quit
# This is event handling instate "S_PLAYING"
#==============================================================================        
        elif self.state == S_PLAYING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"playing", "from":self.me, "target":self.peer,\
                                         "from_id":self.id, 'content':my_msg, "time":time.time()}))

            for event in pygame.event.get():
                self.screen.blit(self.background, (0, 0))
                if self.id == 'mouse':
                    # screen.blit(title_mouse, (0,500))
                    if event.type == QUIT:
                        pygame.quit()
                        self.state = S_LOGGEDIN
                        self.peer = ""
                        mysend(self.s, json.dumps({"action":"g_disconnect","id":self.id}))

                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            pygame.quit()

                            self.disconnect()
                            self.state = S_LOGGEDIN
                            self.g_peer = ''
                        elif event.key == K_SPACE:
                            self.id = 'bomb'
                        else:
                            try:
                                self.screen.blit(self.mouse, mouse_d[chr(event.key)])
                                mysend(self.s,
                                       json.dumps({"action": "playing", "from": self.me, "target": self.peer, \
                                                   "from_id": self.id, "location": chr(event.key),
                                                   "time": time.time()}))
                            except:
                                pass
                elif self.id == 'bomb':
                        # screen.blit(title_mouse, (0,500))
                    if event.type == QUIT:
                        pygame.quit()
                        self.state = S_LOGGEDIN
                        self.peer = ""
                        mysend(self.s, json.dumps({"action": "g_disconnect", "id":self.id}))
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            pygame.quit()
                            self.disconnect()
                            self.state = S_LOGGEDIN
                            self.g_peer = ''
                        elif event.key == K_SPACE:
                            self.id = 'mouse'
                        else:
                            try:
                                self.screen.blit(self.bomb, bomb_d[chr(event.key)])
                                mysend(self.s,
                                       json.dumps({"action": "playing", "from": self.me, "target": self.peer, \
                                                   "from_id": self.id, "location": chr(event.key),
                                                   "time": time.time()}))
                            except:
                                pass

                elif self.id == 'hammer':
                    # screen.blit(title_hammer, (0,500))
                    if event.type == QUIT:
                        pygame.quit()
                        self.state = S_LOGGEDIN
                        self.peer = ""
                        mysend(self.s, json.dumps({"action":"g_disconnect", "id":self.id}))
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            pygame.quit()
                            self.disconnect()
                            self.state = S_LOGGEDIN
                            self.g_peer = ''
                        else:
                            try:
                                self.screen.blit(self.hammer, hammer_d[chr(event.key)])
                                mysend(self.s, json.dumps({"action": "playing", "from": self.me, "target": self.peer, \
                                                           "from_id": self.id, "location": chr(event.key),
                                                           "time": time.time()}))
                            except:
                                pass


            if len(peer_msg) > 0:  # peer's stuff, coming in
                # print("before", peer_msg)
                peer_msg = json.loads(peer_msg)
                
                if "scorechange" in peer_msg.keys() and peer_msg["scorechange"] != 0:
                    #self.out_msg += str(peer_msg['from'])
                    self.out_msg += self.id + " side gets " + str(peer_msg["scorechange"]) + " points!"
#                if "scorechange" in peer_msg.keys() :
#                    self.out_msg += self.id + " side gets " + str(peer_msg["scorechange"]) + " points!"

                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + ")joined\n"
                elif peer_msg["action"] == "g_disconnect":
                    self.state = S_LOGGEDIN
                    self.peer = ""
                    self.out_msg += 'your score is: ', peer_msg['score']
#                    print("you score is:", peer_msg["score"])
                else:
                    peer_id = peer_msg['from_id']
                    peer_location = peer_msg['location']
                    if peer_id == 'mouse':
                        try:
                            self.screen.blit(self.mouse, mouse_d[peer_location])
                        except:
                            pass
                    elif peer_id == 'bomb':
                        try:
                            self.screen.blit(self.bomb, bomb_d[peer_location])
                        except:
                            pass
                    elif peer_id == 'hammer':
                        try:
                            self.screen.blit(self.hammer, hammer_d[peer_location])
                        except:
                            pass

    #                    peer_msg = json.loads(peer_msg)
    #                    peer = peer_msg['from']
                    #pygame.init()
            if self.state == S_PLAYING:
                pygame.display.update()
                #if self.id!='hammer':
                #    pygame.time.delay(1000)



             # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu            
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
