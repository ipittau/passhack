from urllib.request import urlopen, Request
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify  # type: ignore
import threading
from datetime import datetime
from htmldom import htmldom
import re


# datetime object containing current date and time
now = datetime.now()
previous_sis = 0

def check_availability():
    result = False
    text = ""
    number_sis = 0
    try:
        url = Request("https://www.passaportonline.poliziadistato.it/CittadinoAction.do?codop=resultRicercaRegistiProvincia&provincia=TO", 
            headers={'User-Agent': 'Mozilla/5.0'})

        # perform the get request and store it in a var
        response = urlopen(url).read()
        
        response_str = str(response)
        #print(response_str)
        dom = htmldom.HtmlDom()
        dom = dom.createDom(response_str)

        regular_expression = re.compile(r'.*data=(\d\d\-\d\d\-\d\d\d\d)')

        rows = dom.find("tr[class=data]")
        #print (rows.html())
        for site in rows:
            disp = site.children("td[headers=disponibilita]")
            descr = site.children("td[headers=descrizione]")
            if disp.text() == "Si":
                #print(descr.text() + " " + disp.text())
                selection = site.children("td[headers=selezionaStruttura]")
                #print (selection.text())
                available_date = regular_expression.findall(selection.text())
                if len(available_date) == 1:
                    print(descr.text() + ": " + available_date[0])
                    

            #print (site.find("td[headers=disponibilita]").html())



        number_sis = response_str.count(">Si<")
        number_nos = response_str.count(">No<")

        if (number_nos+number_sis) != 14:
            Notify.init("App Name")
            Notify.Notification.new("Login scaduto").show()
            return -1
        # check if new hash is same as the previous hash
        if number_sis == 0:
            #continue
            print("nothing changed")
            text="Posti esauriti"
        else:
            if number_sis >= 1:
                # notify
                text="{0}: Posti disponibili {1}".format(datetime.now(),number_sis)
                print(text)
                result = True
    # To handle exceptions
    except Exception as e:
        print (e)
        text="Error checking"
    return number_sis

def start_timer():
    threading.Timer(1.0, timer_handler).start()

def timer_handler():
    global previous_sis
    now_sis = check_availability()
    if now_sis > previous_sis:
        Notify.init("App Name")
        Notify.Notification.new("Ci sono {0} posti".format(now_sis)).show()
        
    previous_sis = now_sis
    
    #next loop do not inform nobody
    start_timer()

start_timer()
#check_availability()