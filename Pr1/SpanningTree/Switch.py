"""
/*
 * Copyright © 2022 Georgia Institute of Technology (Georgia Tech). All Rights Reserved.
 * Template code for CS 6250 Computer Networks
 * Instructors: Maria Konte
 * Head TAs: Johann Lau and Ken Westdorp
 *
 * Georgia Tech asserts copyright ownership of this template and all derivative
 * works, including solutions to the projects assigned in this course. Students
 * and other users of this template code are advised not to share it with others
 * or to make it available on publicly viewable websites including repositories
 * such as GitHub and GitLab. This copyright statement should not be removed
 * or edited. Removing it will be considered an academic integrity issue.
 *
 * We do grant permission to share solutions privately with non-students such
 * as potential employers as long as this header remains in full. However,
 * sharing with other current or future students or using a medium to share
 * where the code is widely available on the internet is prohibited and
 * subject to being investigated as a GT honor code violation.
 * Please respect the intellectual ownership of the course materials
 * (including exam keys, project requirements, etc.) and do not distribute them
 * to anyone not enrolled in the class. Use of any previous semester course
 * materials, such as tests, quizzes, homework, projects, videos, and any other
 * coursework, is prohibited in this course.
 */
"""

# Spanning Tree Protocol project for GA Tech OMSCS CS-6250: Computer Networks
#
# Copyright 2023 Vincent Hu
#           Based on prior work by Sean Donovan, Jared Scott, James Lohse, and Michael Brown

from Message import Message
from StpSwitch import StpSwitch


class Switch(StpSwitch):
    """
    This class defines a Switch (node/bridge) that can send and receive messages
    to converge on a final, loop-free spanning tree. This class
    is a child class of the StpSwitch class. To remain within the spirit of
    the project, the only inherited members or functions a student is permitted
    to use are:

    switchID: int
        the ID number of this switch object
    links: list
        the list of switch IDs connected to this switch object)
    send_message(msg: Message)
        Sends a Message object to another switch)

    Students should use the send_message function to implement the algorithm.
    Do NOT use the self.topology.send_message function. A non-distributed (centralized)
    algorithm will not receive credit. Do NOT use global variables.

    Student code should NOT access the following members, otherwise they may violate
    the spirit of the project:

    topolink: Topology
        a link to the greater Topology structure used for message passing
    self.topology: Topology
        a link to the greater Topology structure used for message passing
    """

    def __init__(self, switchID: int, topolink: object, links: list):
        """
        Invokes the super class constructor (StpSwitch), which makes the following
        members available to this object:

        switchID: int
            the ID number of this switch object
        links: list
            the list of switch IDs connected to this switch object
        """
        super(Switch, self).__init__(switchID, topolink, links)
        # TODO: Define instance members to keep track of which links are part of the spanning tree
        # a. a variable to store the switch ID that this switch sees as the root,
        self.root = self.switchID

        # b. a variable to store the distance to the switch’s root,
        self.distance = 0

        # c. a list or other datatype that stores the “active links” (only the links to
        # neighbors that are in the spanning tree).
        self.activeLinks = []

        # d. a variable to keep track of which neighbor it goes through to get to the root
        self.pioneer = self.switchID

    def process_message(self, message: Message):
        """
        Processes the messages from other switches. Updates its own data (members),
        if necessary, and sends messages to its neighbors, as needed.

        message: Message
            the Message received from other Switches
        """
        # TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.
        toUpdatePath = False
        examinedDist = message.distance + 1

        # A. 1. Update root if a lower claimedRoot is received
        #    2. Update distance: 2.a) Updated the root
        if message.root < self.root:
            toUpdatePath = True
        elif message.root == self.root:
            # 2.b) A shorter path to the same root
            if examinedDist < self.distance:
                toUpdatePath = True
            # 2. c) Update pioneer (same distance but lower switch ID)
            elif examinedDist == self.distance and message.origin < self.pioneer:
                toUpdatePath = True

        # B. Update active links
        if toUpdatePath:
            self.root = message.root
            self.distance = examinedDist

            # B. 1. New path to root: remove old link (self.pioneer) and add new link (message.origin)
            if message.origin != self.pioneer:
                if self.pioneer in self.activeLinks:
                    self.activeLinks.remove(self.pioneer)
                self.pioneer = message.origin
                if message.origin not in self.activeLinks:
                    self.activeLinks.append(message.origin)

        # B. 2. pathThrough=True (child): add originID
        if message.pathThrough and message.origin not in self.activeLinks:
            self.activeLinks.append(message.origin)

        # B. 3. pathThrough=False && originID in activeLinks: remove originID from activeLinks if not pioneer
        if not message.pathThrough and message.origin != self.pioneer and message.origin in self.activeLinks:
            self.activeLinks.remove(message.origin)

        # C. Send message to neighbors:
        # 1. Should use the send_message(). Do NOT use self.topology.send_message()
        # 2. pathThrough=True: origin switch goes through destination to reach claimedRoot
        # 3. Stop sending messages when ttl=0; Decrement the ttl every time
        if message.ttl > 0:
            for link in self.links:
                newMessage = Message(self.root, self.distance, self.switchID,
                                     link, link == self.pioneer, message.ttl-1)
                self.send_message(newMessage)

    def generate_logstring(self):
        """
        Logs this Switch's list of Active Links in a SORTED order

        returns a String of format:
            SwitchID - ActiveLink1, SwitchID - ActiveLink2, etc.
        """
        # TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked
        #      only after the simulation is complete.  Output the links included in the
        #      spanning tree by INCREASING destination switch ID on a single line.
        #
        #      Print links as '(source switch id) - (destination switch id)', separating links
        #      with a comma - ','.
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #
        #      A full example of a valid output file is included (Logs/) in the project skeleton.

        logs = []
        for activeLink in sorted(self.activeLinks):
            logs.append(f"{self.switchID} - {activeLink}")
        # print(", ".join(logs))
        return ", ".join(logs)
