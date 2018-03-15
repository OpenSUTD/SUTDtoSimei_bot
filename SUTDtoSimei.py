#############################################################################
# This bot determines the optimal bus to take when going to Simei from SUTD #
#############################################################################

import requests
import json
import math
import telegram
import botinfo
import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

#initialization of variables stored in seperate file for security reasons
TOKEN = botinfo.TOKEN

#initialization of stuff for the bot to run
PORT = int(os.environ.get('PORT', '5000'))
bot = telegram.Bot(token = TOKEN)
bot.setWebhook(url = "https://sutdtosimei-bot.herokuapp.com/" + TOKEN)
updater = Updater(token = TOKEN)
dispatcher = updater.dispatcher

#This function queries an API to get the arrival time of the next bus 5 at the SUTD bus stop
#Returns the arrival time in minutes
def get_bus5_time():
	r = requests.get("https://arrivelah.herokuapp.com/?id=96049")
	data = r.text
	data = json.loads(data)
	services = data['services']
	for service in services:
		if service["no"] == "5":
			service5 = service

	next_bus5_time_ms = service5['next']['duration_ms']
	next_bus5_time_min = math.floor(next_bus5_time_ms/60/1000)

	return next_bus5_time_min

#This function queries an API to get the arrival time of the next bus 20 at the SUTD bus stop
#Returns the arrival time in minutes
def get_bus20_time():
	r = requests.get("https://arrivelah.herokuapp.com/?id=96441")
	data = r.text
	data = json.loads(data)
	service20 = data['services'][0]

	next_bus20_time_ms = service20['next']['duration_ms']
	next_bus20_time_min = math.floor(next_bus20_time_ms/60/1000)

	return next_bus20_time_min

#Function executed when user calls start command, gives the user some info about what the bot does
def start(bot,update):
	print("in start")
	bot.sendMessage(chat_id = update.message.chat_id,
					message = "Hello %s! I will help you check the arrival times of bus 20 and bus 5 going towards Simei from SUTD.\n"
							  "To get the bus timings, just type /gosimei."%update.message.from_user.first_name)

dispatcher.add_handler(CommandHandler('start', start))

#This function compares the time needed for bus 5 and bus 20 to come, and returns appropriate advice for the user
def getAdvice(bus5_time, bus20_time):
	if bus5_time < 3 and bus20_time < 3:
		return "Seems like both buses are coming soon, better hurry to whichever bus stop is nearer!"

	if bus5_time < 3:
		return "Seems like bus 5 is coming soon, better hurry!"

	if bus20_time < 3:
		return "Seems like bus 20 is coming soon, better hurry!"

	if bus20_time < bus5_time:
		faster_bus = "bus 20"

	else:
		faster_bus = "bus 5"

	return "Seems like %s is coming sooner, guess you should go for that one"%faster_bus


#Function that checks both the bus 5 and 20 timings and sends them to the user
def goSimei(bot,update):
	bus5_time = get_bus5_time();
	bus20_time = get_bus20_time();
	advice = getAdvice(bus5_time, bus20_time)
	bot.sendMessage(chat_id = update.message.chat_id, 
					message = "Bus 5 is arriving in %d minutes.\n"
							  "Bus 20 is arriving in %d minutes.\n"
							  "%s"%(bus5_time,bus20_time,advice))

dispatcher.add_handler(CommandHandler('gosimei', goSimei))

updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.setWebhook("https://sutdtosimei-bot.herokuapp.com/" + TOKEN)
updater.idle()


