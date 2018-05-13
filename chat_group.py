# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 09:58:31 2015

@author: zhengzhang
"""
S_ALONE = 0
S_TALKING = 1
S_PLAYING = 2

#==============================================================================
# Group class:
# member fields:
#   - An array of items, each a Member class
#   - A dictionary that keeps who is a chat group
# member functions:
#    - join: first time in
#    - leave: leave the system, and the group
#    - list_my_peers: who is in chatting with me?
#    - list_all: who is in the system, and the chat groups
#    - connect: connect to a peer in a chat group, and become part of the group
#    - disconnect: leave the chat group but stay in the system
#==============================================================================

class Group:

    def __init__(self):
        self.members = {}
        self.chat_grps = {}
        self.grp_ever = 0

    def join(self, name):
        self.members[name] = S_ALONE
        return

    def is_member(self, name):
        return name in self.members.keys()

    def leave(self, name):
        self.disconnect(name)
        del self.members[name]
        return

    def find_group(self, name):
        found = False
        group_key = 0
        for k in self.chat_grps.keys():
            if name in self.chat_grps[k]:
                found = True
                group_key = k
                break
        return found, group_key

    def connect(self, me, peer):
        peer_in_group = False
        #if peer is in a group, join it
        peer_in_group, group_key = self.find_group(peer)
        if peer_in_group == True:
            print(peer, "is talking already, connect!")
            self.chat_grps[group_key].append(me)
            self.members[me] = S_TALKING
        else:
            # otherwise, create a new group
            print(peer, "is idle as well")
            self.grp_ever += 1
            group_key = self.grp_ever
            self.chat_grps[group_key] = []
            self.chat_grps[group_key].append(me)
            self.chat_grps[group_key].append(peer)
            self.members[me] = S_TALKING
            self.members[peer] = S_TALKING
        print(self.list_me(me))
        return self.chat_grps

    def disconnect(self, me):
        # find myself in the group, quit
        in_group, group_key = self.find_group(me)
        if in_group == True:
            self.chat_grps[group_key].remove(me)
            self.members[me] = S_ALONE
            # peer may be the only one left as well...
            if len(self.chat_grps[group_key]) == 1:
                peer = self.chat_grps[group_key].pop()
                self.members[peer] = S_ALONE
                del self.chat_grps[group_key]
        return self.chat_grps

    def list_all(self, me):
        # a simple minded implementation
        full_list = "Users: ------------" + "\n"
        full_list += str(self.members) + "\n"
        full_list += "Groups: -----------" + "\n"
        full_list += str(self.chat_grps) + "\n"
        return full_list

    def list_all2(self, me):
        print("Users: ------------")
        print(self.members)
        print("Groups: -----------")
        print(self.chat_grps, "\n")
        member_list = str(self.members)
        grp_list = str(self.chat_grps)
        return member_list, grp_list

    def list_me(self, me):
        # return a list, "me" followed by other peers in my group
        if me in self.members.keys():
            my_list = []
            my_list.append(me)
            in_group, group_key = self.find_group(me)
            if in_group == True:
                for member in self.chat_grps[group_key]:
                    if member != me:
                        my_list.append(member)
        return my_list

g = Group()
class gGroup(Group):
    def __init__(self, members):
        Group.__init__(members)
        self.g_grps = {}
        self.ggrp_ever = 0
    def g_find_group(self, name):
        found = False
        ggroup_key = 0
        for k in self.g_grps.keys():
            if name in self.g_grps[k]:
                found = True
                ggroup_key = k
                break
        return found, ggroup_key
    def game_connect(self, me, peer):
        peer_in_ggroup = False
        #if peer is in a group, join it
        peer_in_ggroup, ggroup_key = self.g_find_group(peer)
        if peer_in_ggroup == True:
            print(peer, "is online, let's start!")
            self.chat_grps[group_key].append(me)
            self.members[me] = S_TALKING
        else:
            # otherwise, create a new group
            print(peer, "is idle as well")
            self.ggrp_ever += 1
            group_key = self.ggrp_ever
            self.g_grps[ggroup_key] = []
            self.g_grps[ggroup_key].append(me)
            self.g_grps[ggroup_key].append(peer)
            self.members[me] = S_PLAYING
            self.members[peer] = S_PLAYING
        print(self.g_list_me(me))
        return self.chat_grps
    def game_disconnect(self, me):
                 # find myself in the group, quit
         in_group, group_key = self.find_group(me)
         if in_group == True:
            self.chat_grps[group_key].remove(me)
            self.members[me] = S_ALONE
            # peer may be the only one left as well...
            if len(self.chat_grps[group_key]) == 1:
                peer = self.chat_grps[group_key].pop()
                self.members[peer] = S_ALONE
                del self.chat_grps[group_key]
            return self.chat_grps
    def g_list_me(self, me):
        # return a list, "me" followed by other peers in my group
         if me in self.members.keys():
            my_list = []
            my_list.append(me)
            in_group, group_key = self.g_find_group(me)
            if in_group == True:
                for member in self.g_grps[group_key]:
                    if member != me:
                        my_list.append(member)
            return my_list