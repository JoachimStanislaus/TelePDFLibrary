import logging
import json
from os import name
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, conversationhandler
from telegram.files.document import Document

BookDict = {}
UserList = {}

class Userr ():
    def __init__(self , notes = {}) -> None:
        self.notes = notes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

BOOKCHOICE= range(1)
BOOKNAME, BOOKFILE = range(2)

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    register_user(update.message.chat_id)
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! Welcome to the pdf library where you can read a collection of books and remember where you left off\! /help for more info',
        reply_markup=ForceReply(selective=True),
    )

def register_user(uid):
    global UserList
    with open('UserList.txt') as f:
        data = json.load(f)
    UserList = data
    UserL = list(UserList.keys())
    uid = str(uid)
    verify = True
    if len(UserL) >= 0 :
        for name in UserL:
            if uid == name:
                verify = False
                print("User already in system")
                break
    if verify == True:
        UserList[uid] = {}
        with open('UserList.txt', 'w') as file:
            file.write(json.dumps(UserList))

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Hello! Here are list of commands\n/Books for a list of books\n/Remember to remember where you left off')

def remembernote(update:Update, context: CallbackContext) -> None:
    update.message.reply_text("Which book would you like to save a note under?\n/skip to skip")
    update.message.reply_text(booklist())
    return BOOKNAME

def remembernote1(update:Update, context: CallbackContext) -> None:
    global bname
    bname = (update.message.text).lower()
    update.message.reply_text("What is your note?")
    return BOOKFILE

def remembernote2(update:Update, context: CallbackContext) -> None:
    bnote = update.message.text
    nameregistered = False
    global UserList
    with open('UserList.txt') as f:
        data = json.load(f)
    UserList = data
    UserL = list(UserList.keys())
    for name in UserL:
        if str(update.message.chat_id) == name:
            CurrentUser = name
            break
    blist = (UserList[CurrentUser])
    blist[bname]= bnote
    with open('UserList.txt', 'w') as file:
            file.write(json.dumps(UserList))
    update.message.reply_text("Saved note...")
    return ConversationHandler.END

def booknote(update:Update, context: CallbackContext, book):
    with open('UserList.txt') as f:
        data = json.load(f)
    UserList = data
    UserL = list(UserList.keys())
    for name in UserL:
        if str(update.message.chat_id) == name:
            CurrentUser = name
            break
    blist = (UserList[CurrentUser])
    if book in blist:
        pagenumber = blist[book]
        return pagenumber
    else:
        pagenumber = " "
        return pagenumber

def booklist():
    global BookDict
    with open('BookDict.txt') as f:
        data = json.load(f)
    BookDict = data
    if len(BookDict)!= 0:
        x = 0
        namestring = ""
        bookname = list(BookDict.keys())
        for name in bookname:
            x += 1
            namestring = namestring + str(x) + ". " + name + "\n"
    else:
        namestring = "There are currently no books available!"
    return namestring


def books(update: Update, context: CallbackContext) -> None:
    if booklist() == "There are currently no books available!":
        update.message.reply_text(booklist())
        return ConversationHandler.END
    else:
        update.message.reply_text(booklist())
        update.message.reply_text('What book would you like to read?\n/skip to skip')
        return BOOKCHOICE

def bookchoice(update: Update, context: CallbackContext) -> None:
    bookname = list(BookDict.keys())
    sendPDF = False
    msg = (update.message.text).lower()
    for name in bookname:
        if msg == (name.lower()):
            choice = name
            sendPDF = True
            break

    if sendPDF == True:
        documentpath ='Books/' + (BookDict[choice]) 
        update.message.reply_document(caption=booknote(update,context,choice.lower()), document=open(documentpath, 'rb'))
        return ConversationHandler.END
    elif sendPDF == False:
        update.message.reply_text('we do not have or recognise that book in our database, Try Again!')
        return ConversationHandler.END
        

def addbook(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Name of book you would like to add?/skip to skip')
    return BOOKNAME

def addbook1(update: Update, context: CallbackContext) -> None:
    global addb
    addb = update.message.text
    update.message.reply_text('Send PDF File... Or /skip to skip')
    return BOOKFILE

def downloadPDF(update: Update, context: CallbackContext) -> None:
    global BookDict
    dl = True
    docname = update.message.document.file_name
    with open('BookDict.txt') as f:
        data = json.load(f)
    BookDict = data
    bookname = list(BookDict.values())
    if len(bookname) != 0:
        for name in bookname:
            if name == docname:
                update.message.reply_text('Book is already inside system')
                dl = False
                break
    if dl == True:    
        update.message.reply_text('Adding Book to the system!')
        BookDict[addb] = docname
        with open('BookDict.txt', 'w') as file:
            file.write(json.dumps(BookDict))
        context.bot.get_file(update.message.document).download(custom_path='C:/Users/Joachim/Desktop/Coding Projects/Python Projects/ThePDFLibrary_bot/Books/{}'.format(docname))
        update.message.reply_text('Book is added to the system!')
    return ConversationHandler.END

def skip(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text('Ok I Understand, What do you want to do instead?')
    return ConversationHandler.END

def notes_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Which Book note would you like to retrieve?')
    return BOOKNAME

def notes_command1(update: Update, context: CallbackContext) -> None:
    msg = (update.message.text).lower()
    update.message.reply_text(booknote(update,context,msg))



def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("2104101224:AAFypLDONYfDBYSGIddYSpuL7nwJQ-CLmdQ")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    conv_handler = ConversationHandler(
        allow_reentry= True ,
        entry_points=[CommandHandler('books', books)],
        states={
            BOOKCHOICE: [MessageHandler((Filters.text), bookchoice), CommandHandler('skip', skip)]
        },fallbacks=[CommandHandler('cancel', start)])

    conv_handler1 = ConversationHandler(
        entry_points=[CommandHandler('AddBook', addbook)],
        states={
            BOOKNAME: [MessageHandler((Filters.text), addbook1), CommandHandler('skip', skip)],
            BOOKFILE: [MessageHandler((Filters.document), downloadPDF), CommandHandler('skip', skip)]
        },fallbacks=[CommandHandler('cancel', start)])

    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('remember', remembernote)],
        states={
            BOOKNAME: [MessageHandler((Filters.text), remembernote1), CommandHandler('skip', skip)],
            BOOKFILE: [MessageHandler((Filters.text), remembernote2), CommandHandler('skip', skip)]
        },fallbacks=[CommandHandler('cancel', start)])
    
    conv_handler3 = ConversationHandler(
        entry_points=[CommandHandler("notes", notes_command)],
        states={
            BOOKNAME: [MessageHandler((Filters.text), notes_command1), CommandHandler('skip', skip)]
        },fallbacks=[CommandHandler('cancel', start)])

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(conv_handler1)
    dispatcher.add_handler(conv_handler2)
    dispatcher.add_handler(conv_handler3)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()