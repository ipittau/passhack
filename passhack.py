from telegram.ext import Updater
from telegram.ext import CommandHandler
from urllib.request import urlopen, Request
#import gi
#gi.require_version('Notify', '0.7')
#from gi.repository import Notify  # type: ignore
import threading
from datetime import datetime
from htmldom import htmldom
import logging

import re


# datetime object containing current date and time
now = datetime.now()
previous_sis = 0
users = dict()

def start(update, context):
    
   update.message.reply_text("Ciao, sono qui per avvisarti quando ci sono posti disponibili per il rinnovo del passaporto in povincia di Torino\n \
   Usa /register per registrati al servizio; \n \
   Usa /unregister per cancellarti dal servizio; \n \
   Usa /verbose se vuoi essere annoiato dalle mie verifiche; \n \
   Usa /quiet se ti sei rotto delle mie notizie; \n \
   Usa /help se vuoi vedere di nuovo questo messaggio;")

def register(update, context):
    global users
    print ("Registering {0}".format(update.effective_chat.id))
    
    if len(users) == 0:
        start_timer()

    user = update.effective_chat.id

    if user in users.keys():
        updater.bot.send_message(chat_id=user, text="Sei già dei nostri")
    else:
        #new user
        users[user] = {'verbose':False}
        updater.bot.send_message(chat_id=user, text="Ti sei registrato al servizio")

def unregister(update, context):
    global users
    print ("Unregistering {0}".format(update.effective_chat.id))
    
    user = update.effective_chat.id

    if user in users.keys():
        users.pop(user)
        updater.bot.send_message(chat_id=user, text="Fatto!")
    else:
        updater.bot.send_message(chat_id=user, text="Non eri registrato, ma va bene lo stesso")

def verbose(update, context):
    global users
    user = update.effective_chat.id
    if user in users.keys():
        users[user] = {'verbose':True}

def quiet(update, context):
    global users
    user = update.effective_chat.id
    if user in users.keys():
        users[user] = {'verbose':False}

def check_availability():
    result = False
    text = ""
    number_sis = 0
    places_and_date = ""
    try:
        url = Request("https://www.passaportonline.poliziadistato.it/CittadinoAction.do?codop=resultRicercaRegistiProvincia&provincia=TO", 
            headers={'User-Agent': 'Mozilla/5.0'})

        # perform the get request and store it in a var
        response = urlopen(url).read()
        response_str = str(response)


        #print(response_str)
        
        #put the response on the html parser
        dom = htmldom.HtmlDom()
        dom = dom.createDom(response_str)

        #this regexp extract the data from the link of the button available only when some day is avilable
        regular_expression = re.compile(r'.*data=(\d\d\-\d\d\-\d\d\d\d)')


        #find all questuras
        rows = dom.find("tr[class=data]")

        #print (rows.html())
        #for each questura
        for site in rows:
            #availability si o no
            disp = site.children("td[headers=disponibilita]")
            #name of the questura
            descr = site.children("td[headers=descrizione]")
            if disp.text() == "Si":
                #print(descr.text() + " " + disp.text())
                #take the button, on the href there is the data! hack hack
                selection = site.children("td[headers=selezionaStruttura]")
                print (selection.text())
                print("--------")
                available_date = regular_expression.findall(selection.text())
                #sometimes the link is available but appointement expired and data is not present anymore
                if len(available_date) == 1:
                    places_and_date += descr.text() + ": " + available_date[0] + "\n"
                    print(descr.text() + ": " + available_date[0])
                    

            #print (site.find("td[headers=disponibilita]").html())

        
        #the Sis is needed since "Questura of Torino" has always a fake day free
        number_sis = response_str.count(">Si<")
        number_nos = response_str.count(">No<")

        #old code if you're using it only without telegram
        #check if the len of the table of questuras is correct 14 places
        if (number_nos+number_sis) != 14:
            #Notify.init("App Name")
            #Notify.Notification.new("Login scaduto").show()
            return -1, ""
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
    return number_sis, places_and_date

def start_timer():
    threading.Timer(1.0, timer_handler).start()

def timer_handler():
    global previous_sis
    now_sis, text = check_availability()

        
    for user in users.keys():
        #tricky we see if the number of Si is bigger than before!
        if now_sis > previous_sis or users[user]['verbose']:
            updater.bot.send_message(chat_id=user, text=text)
        
    previous_sis = now_sis
    
    #next loop do not inform nobody
    start_timer()

updater = Updater(token='2037454689:AAH4egaAzo_JBBgmZpX2mDO5yz4_wHoZT3Q', use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
start_handler = CommandHandler('start', start)

dispatcher.add_handler(start_handler)

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', start))
dispatcher.add_handler(CommandHandler('register', register))
dispatcher.add_handler(CommandHandler('unregister', unregister))
dispatcher.add_handler(CommandHandler('verbose', verbose))
dispatcher.add_handler(CommandHandler('quiet', quiet))

updater.start_polling()

updater.idle()