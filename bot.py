import city
import metro
import restaurants as rs
from typing import List, Tuple, Optional
from telegram.update import Update
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


"""
Template file for bot.py module.
"""


"""
Module that contains the code related to the implementation for the
construction of the Telegram bot, that reacts to user commands in order to
guide them. Uses the city and restaurants modules.
"""


TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


# Global variables with the escencial information for the bot
restaurants: rs.Restaurants = rs.read()
Streets: city.OsmnxGraph = city.get_osmnx_graph()
Metro: metro.MetroGraph = metro.get_metro_graph()
City: city.CityGraph = city.build_city_graph(Streets, Metro)


def register_user(update: Update, context: CallbackContext):
    """Registers a new user (with some basic attributes) in the bot's user
    dictionary."""

    user_id = update.effective_chat.id
    user_name = update.effective_chat.first_name
    matching_restaurants: rs.Restaurants = []
    context.user_data[user_id] = {'Name': user_name,
                                  'User restaurants': matching_restaurants,
                                  'Coordinates': [0.0, 0.0]}


def verify_user(update: Update, context: CallbackContext):
    """It checks if the user already exists within the bot's dictionary
    and, if not, adds it."""

    user_id = update.effective_chat.id
    if user_id not in context.user_data:
        register_user(update, context)


def start(update: Update, context: CallbackContext):
    """Command to start the bot that sends a welcome message to the user."""

    verify_user(update, context)

    start_info = '''
Welcome to *Metrobot*

I am designed to guide you through the city of Barcelona ❤️💙
in the search for a restaurant of your choice.

For the restaurant you choose, you will receive a map with the
shortest possible route in terms of time to your destination.
Note: The route uses only the metro service 🚥, in addition to
parts of the route walking.

In case you are new or lost, to consult the information of all
the commands type /help.❔

It is important to know your location, send it please. It's
only in order to calculate the fastest possible route. 🏁

'''
    update.message.reply_text("Hi %s" % context.user_data[update.effective_chat.id]['Name'])
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_info, parse_mode="Markdown")
    context.bot.send_message(chat_id=update.effective_chat.id, text="🤖")


def help(update: Update, context: CallbackContext):
    """Command to send a help message to the user with the description of the
    commands."""

    help_info = '''

*/author:* Writes a message with the names of the authors of Metro-Bot.

*/find: <query>* Finds the restaurants that satisfy the query(s) and saves
them in a list of matching restaurants. Returns the name of the
first 12 restaurants in the list of matching restaurants. If you want,
there is an option to see the whole list of matching restaurants. If an
error occurs, it displays an error text.

*/info: <number>* Shows the complete information of the restaurant
specified by its number (index) that appears in the list of
results obtained with the /find command. If an error occurs, it
displays an error text.

*/guide: <number>* Estimates the shortest route
(in time) to the restaurant specified by its number (index) that appears
in the list of results obtained with the /find command. Sends an image
of the route. The starting point is red and the destination is indicated
in purple. The estimated time of the route is also displayed.
(Remember, this is just an estimate).
If an error occurs, it displays an error text.

Remember, I need your location to work correctly...

'''
    update.message.reply_text(help_info, parse_mode="Markdown")


def author(update: Update, context: CallbackContext):
    """Writes a message with the names of the authors of Metro-Bot."""

    author_info = '''
Enric Millán Iglesias & Juan Pablo Zaldivar.

Universitat Politècnica de Catalunya, 2022.
'''
    update.message.reply_text(author_info, parse_mode="Markdown")
    context.bot.send_message(chat_id=update.effective_chat.id, text="🥸")


def find(update: Update, context: CallbackContext):
    """Finds the restaurants that satisfy the query and saves them in a list
    of matching restaurants. Returns the name of the first 12 restaurants in
    the list of matching restaurants. If an error occurs, it displays an error
    text."""

    verify_user(update, context)

    try:
        user_restaurants: rs.Restaurant = []
        # finds matching restaurants for all query arguments.
        for i in range(len(context.args)):
            query = str(context.args[i])
            if i == 0:
                user_restaurants = rs.find(query, restaurants)
            else:
                user_restaurants = rs.find(query, user_restaurants)

        if len(user_restaurants) == 0:
            text: str = "No results were found, sorry.\nTry another word."
            update.message.reply_text(text)
            context.bot.send_message(chat_id=update.effective_chat.id, text="😔")
        else:
            i: int = 0
            txt: str = "Choose your restaurant:\n"
            while i < len(user_restaurants) and i < 12:
                txt += str(i + 1) + ". "
                txt += str(user_restaurants[i].name) + "\n"
                i += 1
            update.message.reply_text(txt)

            txt2: str = "Do you need more options?\n"
            txt2 += "Click 'Yes' to see some other results."

            # Option to show the whole list of matching restaurants.
            if (len(user_restaurants) >= 12):
                buttons = [[InlineKeyboardButton("Yes", callback_data='y')],
                           [InlineKeyboardButton("No", callback_data='n')]]
                update.message.reply_text(
                    txt2, reply_markup=InlineKeyboardMarkup(buttons))

        # Updates the list of matching restaurants for each bot user.
        user_id = update.effective_chat.id
        context.user_data[user_id]['User restaurants'] = user_restaurants

    except Exception as e:
        error = str(e)
        update.message.reply_text(error)
        context.bot.send_message(chat_id=update.effective_chat.id, text=("🤯"))


def queryHandler(update: Update, context: CallbackContext):
    """Writes the rest of the list of restaurants obtained with the /find
    command, if the user has requested it by clicking the 'Yes' in-line-button."""

    query = update.callback_query.data
    update.callback_query.answer()

    verify_user(update, context)

    try:
        if 'y' in query:
            i: int = 12
            txt: str = ""
            user_id = update.effective_chat.id
            restaurants = context.user_data[user_id]['User restaurants']
            while i < len(restaurants):
                txt += str(i+1) + '. '
                txt += str(restaurants[i].name) + '\n'
                i += 1
            txt += "\nThere you go!"
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=txt)
        if 'n' in query:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Fine!")

    except Exception as e:
        error = str(e)
        context.bot.send_message(chat_id=update.effective_chat.id, text=error)
        context.bot.send_message(chat_id=update.effective_chat.id, text="🤯")


def info(update: Update, context: CallbackContext):
    """Shows the complete information of the restaurant specified by its
    number (index) that appears in the list of results obtained with the
    /find command."""

    try:
        if int(context.args[0]) <= 0:
            update.message.reply_text("Index must be a positive integer.")
            context.bot.send_message(chat_id=update.effective_chat.id, text="🤯")
            return

        verify_user(update, context)

        num = int(context.args[0]) - 1
        user_id = update.effective_chat.id
        restaurants = context.user_data[user_id]['User restaurants']

        txt: str = "Restaurant information: \n"
        txt += "Restaurant name 🍴: "
        txt += str(restaurants[num].name) + "\n"
        txt += "Restaurant address 🗺: "
        txt += str(restaurants[num].addresses_road_name)
        txt += ", "
        add: str
        add = str(int(restaurants[num].addresses_start_street_number))
        txt += add  # This is done to respect pycodestyle format.
        txt += "\n"
        txt += "Restaurant district 🗺: "
        txt += str(restaurants[num].addresses_district_name) + '\n'
        txt += "Restaurant phone number ☎️: "
        txt += str(restaurants[num].values_value) + "\n"
        txt += "\nRemeber, "
        txt += "I need your location to guide you to this restaurant."
        update.message.reply_text(txt)

    except Exception as e:
        error = str(e)
        update.message.reply_text(error)
        context.bot.send_message(chat_id=update.effective_chat.id, text="🤯")


def where(update: Update, context: CallbackContext):
    """Saves the user's location and sends him a message indicating his/her
    coordinates."""

    verify_user(update, context)

    lat = update.message.location.latitude
    lon = update.message.location.longitude
    update.message.reply_text("Your coordinates: %f, %f" % (lon,
                                                            lat))
    user_id = update.effective_chat.id
    context.user_data[user_id]['Coordinates'] = [lon, lat]


def guide(update: Update, context: CallbackContext):
    """Calculates the fastest route in terms of time from user's location to
    the chosen restaurant location (restaurant is chosen with its
    number (index) that appears in the list of results obtained with the
    /find command.). Sends a photo with the route drawn on a map of the
    City graph."""

    verify_user(update, context)
    user_id = update.effective_chat.id
    lon, lat = context.user_data[user_id]['Coordinates']
    restaurants = context.user_data[user_id]['User restaurants']

    if lon == 0.0 and lat == 0.0:
        update.message.reply_text("You need to send me your location first.\nPlease")
        context.bot.send_message(chat_id=update.effective_chat.id, text="😖")
        return

    try:
        if int(context.args[0]) <= 0:
            update.message.reply_text("Index must be a positive integer.")
            context.bot.send_message(chat_id=update.effective_chat.id, text="🤯")
            return
        num = int(context.args[0]) - 1

        update.message.reply_text("Give me just a sec...")

        # User and restaurant location.
        src: city.Coord = [lon, lat]
        dst_lat = restaurants[num].latitude
        dst_lon = restaurants[num].longitude
        dst: city.Coord = [float(dst_lon), float(dst_lat)]

        path: city.Path = city.find_path(Streets, City, src, dst)
        path_edges: List[Tuple[city.NodeID]] = city.get_edges_from_path(path)

        city.plot_path(City, path, 'path.png', path_edges)  # path image generated.
        context.bot.send_photo(chat_id=update.effective_chat.id,
                               photo=open('path.png', 'rb'))

        time: float = city.travel_time(City)
        city.remove_src_and_dst_nodes(City)
        context.bot.send_message(chat_id=update.effective_chat.id, text="You: 🔴, Restaurant: 🟣")
        txt: str = "Estimated time of %s min.\nGood luck!" % int(time)
        context.bot.send_message(chat_id=update.effective_chat.id, text=txt)

    except Exception as e:
        error = str(e)
        update.message.reply_text(error)
        context.bot.send_message(chat_id=update.effective_chat.id, text="🤯")


def unknown_text(update: Update, context: CallbackContext):
    """Send an error message to the user in case of receiving an
    unrecognized message."""

    update.message.reply_text(
        "Sorry I can't recognize you , you said %s" % update.message.text)


def unknown(update: Update, context: CallbackContext):
    """Send an error message to the user in case of receiving an
    incorrect command."""

    update.message.reply_text(
        "Sorry %s is not a valid command" % update.message.text)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('find', find))
updater.dispatcher.add_handler(CommandHandler('info', info))
updater.dispatcher.add_handler(CommandHandler('guide', guide))
updater.dispatcher.add_handler(CommandHandler('author', author))

updater.dispatcher.add_handler(MessageHandler(Filters.location, where))
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.dispatcher.add_handler(CallbackQueryHandler(queryHandler))

updater.start_polling()
updater.idle()
