# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-
from abc import ABCMeta, abstractmethod
import math
from difflib import SequenceMatcher
import xml.etree.ElementTree as ET

from Tkinter import *
import Tkinter as ttk
from ttk import *


weightVac = {"code": 0.2, "accomodation": 0.1, "hotel": 0.05, "duration": 0.1, "holidaytype": 0.2, "persons": 0.05, "destination": 0.05, "price": 0.1, "transportation": 0.05, "season": 0.1}
weightDvd = {"name": 0.1, "jahr": 0.1, "kategorie": 0.05, "nummer": 0.1, "vorhanden": 0.1, "sprache": 0.05, "hauptdarsteller": 0.05, "preis": 0.1, "ausgeliehen": 0.05, "herkunftsland": 0.1, "regisseur": 0.1, "kurzbeschreibung": 0.1}
weights = {}
k = 5

reader, cases, attributesOnView, weightsSum, cases = "", "", {}, 0.0, []

seasonSimilarity = {"summer": {"winter": 0.0, "autumn": 0.5, "spring": 0.5},
                    "autumn": {"winter": 0.25, "spring": 1, "summer": 0.5},
                    "winter": {"summer": 0.0, "autumn": 0.25, "spring": 0.25},
                    "spring": {"winter": 0.25, "autumn": 1, "summer": 0.5}}

transportSimilarity = {"Car": {"Coach": 0.75, "Plane": 0.0, "Train": 0.25},
                    "Coach": {"Car": 0.75, "Plane": 0.25, "Train": 0.5},
                    "Plane": {"Car": 0.0, "Coach": 0.25, "Train": 0.5},
                    "Train": {"Car": 0.25, "Coach": 0.5, "Plane": 0.5}}

categorySimilarity = {"Action": {"Komödie": 0.25, "Lovestory": 0.0, "Thriller": 0.75},
                    "Komödie": {"Action": 0.25, "Lovestory": 0.25, "Thriller": 0.0},
                    "Lovestory": {"Action": 0.0, "Komödie": 0.25, "Thriller": 0.0},
                    "Thriller": {"Action": 0.75, "Komödie": 0.0, "Lovestory": 0.0}}

seasonForMonth = {
                "January": "spring",
                "February": "spring",
                "March": "spring",
                "April": "summer",
                "May": "summer",
                "June": "summer",
                "July": "autumn",
                "Juhly": "autumn",
                "August": "autumn",
                "September": "autumn",
                "October": "winter",
                "November": "winter",
                "December": "winter"
            }

class AbstractCBR:
    __metaclass__ = ABCMeta

    @abstractmethod
    def similarString(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    @abstractmethod
    def similarFloat(self, a, b):
        #a = a * a
        #b = b * b
        #value = a / math.sqrt(a * b)
        #return value if value <= 1 else value/10
        if a == b:
            return 1
        return 0

    @abstractmethod
    def similarObject(self, a, b, attribute):
        pass

    @abstractmethod
    def createCase(self, entry):
        caseAttributes = {}
        if type(entry) == dict:
            for key, value in entry.items():
                caseAttributes[key] = value
        else:
            for attribute in entry:
                caseAttributes[attribute.tag] = attribute.text
        return caseAttributes



class Reader:
    def __init__(self, filename):
        self.fileList = []
        tree = ET.parse(filename)
        fileBase = tree.getroot()
        if fileBase.tag == "holidaybase":
            for case in fileBase:
                self.fileList.append(Vacation(case))
        elif fileBase.tag == "filme":
            for case in fileBase:
                self.fileList.append(Dvd(case))

    def getCaseList(self):
        return self.fileList



class Dvd(AbstractCBR):
    def __init__(self, film):
        self.attributes = self.createCase(film)
        for key, value in self.attributes.iteritems():

            try:
                if key == "preis":
                    value = float(value)
                else:
                    value = int(value)
            except:
                value = value.encode('utf-8')

            self.attributes[key] = value
            setattr(self, key, value)

        if type(film) != dict:
            #read category from film-Header
            for key, value in film.attrib.items():
                self.attributes[key] = value.encode('utf-8')
                setattr(self, key, value.encode('utf-8'))

    def similarObject(self, a, b, attribute):
        if attribute == "kategorie":
            if a != b:
                return categorySimilarity[a][b]
        return 1.0

    def similarString(self, a, b):
        super(Dvd, self).similarString()

    def similarFloat(self, a, b):
        super(Dvd, self).similarFloat()

    def createCase(self, entry):
        return super(Dvd, self).createCase(entry)

    def setAttribute(self, attr, value):
        self.attributes[attr] = value
        setattr(self, attr, value)

    def __str__(self):
        string = ""
        for ele in self.attributes:
            string += " " + ele + ":" + str(getattr(self, ele))
        return string

    def getBestCases(self, caseList, k):
        compareList = []
        for element in caseList:
            sim = 0
            for key, value in element.attributes.items():
                if self.attributes[key]:
                    if key == "kategorie":
                        # print key, self.similarObject(self.attributes[key], value, key) * weight[key]
                        if self.attributes[key] in categorySimilarity:
                            sim += self.similarObject(self.attributes[key], value, key) * weights[key]
                        else:
                            sim += super(Dvd, self).similarString(self.attributes[key], value) * weights[key]
                    elif isinstance(value, basestring):
                        #print key, super(Dvd, self).similarString(self.attributes[key], value) * weight[key]
                        sim += super(Dvd, self).similarString(self.attributes[key], value) * weights[key]
                    elif isinstance(value, float):
                        # print key, super(Vacation, self).similarFloat(self.attributes[key], value) * weight[key]
                        sim += super(Dvd, self).similarFloat(self.attributes[key], value) * weights[key]
            compareList.append((sim, element))

        return sorted(compareList, key=lambda tup: tup[0], reverse=True)[0:k]



class Vacation(AbstractCBR):
    def __init__(self, vacation):
        self.attributes = self.createCase(vacation)
        for key, value in self.attributes.iteritems():

            try:
                if key != "code":
                    value = float(value)
            except:
                value = value.decode('utf-8')

            if key == "season":
                if self.attributes[key] in seasonSimilarity:
                    self.attributes[key] = seasonForMonth[value]
                    setattr(self, key, seasonForMonth[value])
                else:
                    self.attributes[key] = ""
                    setattr(self, key, "")
            else:
                self.attributes[key] = value
                setattr(self, key, value)

    def similarObject(self, a, b, attribute):
        if attribute == "season":
            if a != b:
                return seasonSimilarity[a][b]
        else:
            if a != b:
                return transportSimilarity[a][b]
        return 1.0

    def similarString(self, a, b):
        super(Vacation, self).similarString()

    def similarFloat(self, a, b):
        super(Vacation, self).similarFloat()

    def createCase(self, entry):
        return super(Vacation, self).createCase(entry)

    def __str__(self):
        string = ""
        for ele in self.attributes:
            string += " " + ele + ":" + str(getattr(self, ele))
        return string

    def getBestCases(self, caseList, k):
        compareList = []
        for element in caseList:
            sim = 0
            for key, value in element.attributes.items():
                if self.attributes[key]:
                    if key == "season" or key == "transportation":
                        #print key, self.similarObject(self.attributes[key], value, key) * weight[key]
                        if self.attributes[key] in transportSimilarity or self.attributes[key] in seasonSimilarity:
                            sim += self.similarObject(self.attributes[key], value, key) * weights[key]
                        else:
                            sim += super(Vacation, self).similarString(self.attributes[key], value) * weights[key]
                    elif isinstance(value, basestring):
                        #print key, super(Vacation, self).similarString(self.attributes[key], value) * weight[key]
                        sim += super(Vacation, self).similarString(self.attributes[key], value) * weights[key]
                    elif isinstance(value, float):
                        #print key, super(Vacation, self).similarFloat(self.attributes[key], value) * weight[key]
                        sim += super(Vacation, self).similarFloat(self.attributes[key], value) * weights[key]
            compareList.append((sim, element))

        return sorted(compareList, key=lambda tup: tup[0], reverse=True)[0:k]


#reader = Reader('DVD-Kiste(xsd).xml')
#reader = Reader('Vacations.xml')

#fall = Dvd({"kategorie":"Thriller", "name":"Fletchers Visionen", "regisseur":"", "hauptdarsteller":"", "herkunftsland":"", "jahr":"", "kurzbeschreibung":"", "vorhanden":"", "ausgeliehen":"", "preis":"", "sprache":"", "nummer":""})

#cases = reader.getCaseList()

#print fall
#print "--------------------------------------\n"
#print fall.getBestCases(cases, 3)[0][1]

def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def compare():
    global weightsSum, cases
    caseAttr = {}
    i = 0
    #math.isclose

    if isclose(weightsSum, 1.0):
        key = ""
        for ele in attributeFrame.winfo_children():
            if i > 1:
                if ele.winfo_class() == "TEntry":
                    if int(ele.grid_info()["column"]) == 2:
                        caseAttr[key] = ele.get()
                    else:
                        weights[key] = float(ele.get())
                else:
                    key = ele["text"]
            i += 1
        if tkvar.get() == "Vacations.xml":
            case = Vacation(caseAttr)
        elif tkvar.get() == "DVD-Kiste(xsd).xml":
            case = Dvd(caseAttr)
        k = int(similarK.get())
        if k > len(cases):
            k = len(cases)
        if k == 0:
            k = 1
        #print case.getBestCases(cases, k)[0:k]
        for ele in case.getBestCases(cases, k)[0:k]:
            print "Ähnlichkeit:     " + str(ele[0])
            print "..................."
            for key, value in ele[1].attributes.items():
                print str(key) + ": " + str(value)
            print "___________________"
    else:
        print "Die Gewichtung muss 1.0 ergeben! Ist aber: " + str(weightsSum)



def showViewAttributes():
    global weightsSum
    weightsSum = 0.0
    if tkvar.get() == "Vacations.xml":
        weights = weightVac
    else:
        weights = weightDvd

    for widget in attributeFrame.winfo_children():
        widget.destroy()


    i = 4
    Label(attributeFrame, text="Fallinfos").grid(row=3, column=2)
    Label(attributeFrame, text="Gewichtung").grid(row=3, column=3)

    for key, value in attributesOnView.items():
        Label(attributeFrame, text=key).grid(row=i, column=1)
        Entry(attributeFrame).grid(row=i, column=2)
        e = Entry(attributeFrame)
        e.insert(0, weights[key])
        e.grid(row=i, column=3)
        weightsSum += weights[key]
        i+=1

    button.pack()


def getCaseAttributes(fileName):
    global cases
    cases = []
    attributesOnView.clear()
    reader = Reader(fileName)
    cases = reader.getCaseList()

    for key, value in cases[0].attributes.items():
        attributesOnView[key] = 0.0
    showViewAttributes()

if __name__ == "__main__":
    root = Tk()
    root.title("Tk dropdown example")

    # Add a grid
    mainframe = Frame(root)
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    mainframe.pack(pady=100, padx=100)

    # Create a Tkinter variable
    tkvar = StringVar(root)
    # List with options
    choices = ['DVD-Kiste(xsd).xml', 'Vacations.xml']

    popupMenu = OptionMenu(mainframe, tkvar, choices[1], *choices, command=getCaseAttributes)

    Label(mainframe, text="Chose a file").grid(row=1, column=1)
    popupMenu.grid(row=2, column=1)
    tkvar.set('')  # set the default option

    attributeFrame = Frame(root)
    attributeFrame.columnconfigure(0, weight=1)
    attributeFrame.rowconfigure(0, weight=1)
    attributeFrame.pack(pady=100, padx=100)

    Label(root, text="k ähnlichste Fälle").pack()
    similarK = Entry(root)
    similarK.insert(0, 1)
    similarK.pack()

    button = Button(root, text="Suche Fall", command=compare)
    root.mainloop()