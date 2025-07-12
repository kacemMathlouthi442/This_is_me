import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    ApplicationBuilder
)
from time import sleep
from UsersDB import *
from KeysDB import *
from Others import *
from Functions import *
from random import randint
import ast
from keepalive import keep_alive
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
import os, logging
from dotenv import load_dotenv

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
logging.basicConfig(level=logging.INFO)
load_dotenv()

keep_alive()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# States for conversation handlers
STEP1, STEP2, STEP3 = range(3)
VICTIM_NUMBER, SPOOF_NUMBER, VICTIM_NAME, SERVICE_NAME, OTP_DIGIT = range(5)


reset_all_user_actions()

#BAN USER
async def keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not get_user_info(user_id, "Banned"):
        if user_id == admin_ID:
            keyboard = [
                [InlineKeyboardButton("🔁 Reset Keys", callback_data="reset"),
                 InlineKeyboardButton("🔑 Get Keys", callback_data="get")],
                [InlineKeyboardButton("🔙 Leave it As is", callback_data="back1")]
            ]
            await update.message.reply_text("🔑 Choose the keys action.", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("🚫 Only admin can use this command.")
print('Bot is running!')

async def cancel_fsm(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if check_subscription(get_user_info(user_id, 'Expiry_Date')):
            if get_user_info(user_id, 'In_Action') == 'NN':
                await update.message.reply_text("❌ There is no process.")
            elif get_user_info(user_id, 'In_Action') == 'CS':
                set_user_value(user_id, 'In_Action', 'NN')
                if 'conversation' in context.user_data:
                    del context.user_data['conversation']
                await update.message.reply_text("❌ Creating custom script process cancelled!")
            else:
                set_user_value(user_id, 'In_Action', 'NN')
                if 'conversation' in context.user_data:
                    del context.user_data['conversation']
                await update.message.reply_text("❌ Creating first call process cancelled!")
        return ConversationHandler.END

async def reset_get_keys(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, "Banned"):
        if user_id == admin_ID:
            keyboard = [
                [InlineKeyboardButton("1 Day", callback_data=f"1DAYZ+{query.data}"),
                 InlineKeyboardButton("3 Days", callback_data=f"3DAYZ+{query.data}")],
                [InlineKeyboardButton("1 Week", callback_data=f"1WEEK+{query.data}"),
                 InlineKeyboardButton("1 Month", callback_data=f"1MNTH+{query.data}")],
                [InlineKeyboardButton("2 Hours", callback_data=f"2HOUR+{query.data}")],
                [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
            ]
            await query.edit_message_text("🔑 Choose the keys type.", reply_markup=InlineKeyboardMarkup(keyboard))

async def choose_keys_type(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, "Banned"):
        if user_id == admin_ID:
            comm = query.data
            key_type = comm[:comm.find('+')]
            action = comm.split('+')[1]
            if action == "get":
                keys = show_valid_keys(key_type)
                await query.edit_message_text(
                    fr"✅ *Available {duration(key_type)} Keys*\: \n" + "\n".join(keys),
                    parse_mode='MarkdownV2')
            else:
                reset_key(key_type)
                await query.edit_message_text(f"✅ {duration(key_type)} reset successfully!")

#BAN USER
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, "Banned"):
        if user_id == admin_ID:
            args = context.args
            if not args:
                await update.message.reply_text("Please provide a user ID to ban.")
                return
            banned_user_id = int(args[0])
            set_user_value(banned_user_id, 'Banned', True)
            await context.bot.send_message(chat_id=banned_ID, 
                                         text=f"{get_user_info(banned_user_id, 'First_Name')} banned successfully!")
            
            # Try to delete messages
            for msg_id in range(update.message.message_id - 50, update.message.message_id):
                try:
                    await context.bot.delete_message(chat_id=banned_user_id, message_id=msg_id)
                except:
                    pass
            
            # Try to ban from channels
            try:
                await context.bot.ban_chat_member(chat_id=main_channel_ID, user_id=banned_user_id)
                await context.bot.ban_chat_member(chat_id=vouches_ID, user_id=banned_user_id)
                await context.bot.send_message(chat_id=banned_ID,
                                             text=f"User {get_user_info(banned_user_id, 'First_Name')} has been banned from the channels.")
            except Exception as e:
                await context.bot.send_message(chat_id=banned_ID,
                                             text=f"Failed to ban user: {str(e)}")
        else:
            await update.message.reply_text("🚫 Only admin can use this command.")

#UNBAN USER
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, "Banned"):
        if user_id == admin_ID:
            args = context.args
            if not args:
                await update.message.reply_text("Please provide a user ID to unban.")
                return
            unbanned_user_id = int(args[0])
            set_user_value(unbanned_user_id, 'Banned', False)
            await context.bot.send_message(chat_id=banned_ID, 
                                         text=f"{get_user_info(unbanned_user_id, 'First_Name')} unbanned successfully!")
            try:
                await context.bot.unban_chat_member(chat_id=main_channel_ID, user_id=unbanned_user_id)
                await context.bot.unban_chat_member(chat_id=vouches_ID, user_id=unbanned_user_id)
                await context.bot.send_message(chat_id=banned_ID,
                                             text=f"User {get_user_info(unbanned_user_id, 'First_Name')} has been unbanned from the channels.")
            except Exception as e:
                await context.bot.send_message(chat_id=banned_ID,
                                             text=f"Failed to unban user: {str(e)}")
        else:
            await update.message.reply_text("🚫 Only admin can use this command.")

async def update_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, "Banned"):
        if user_id == admin_ID:
            global spoofing_numbers, spoof_message
            spoofing_numbers = get_random_lines()
            spoof_message = set_message(spoofing_numbers)
            await update.message.reply_text("✅ Spoofing numbers list Updated Successfully!")
        else:
            await update.message.reply_text("🚫 Only admin can use this command.")

#START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, "Banned"):
        name = update.effective_user.first_name
        if not user_exists(user_id):
            add_user(update.effective_user)
            await context.bot.send_message(
                chat_id=7674917466,
                text=f'🆕 *New user*: [{get_user_count()}]\n'
                     f'*Username*: {escape_markdown(get_user_info(user_id, "Username_Name"))}\n'
                     f'*Name*: `{escape_markdown(get_user_info(user_id, "First_Name"))}`\n'
                     f'*User ID*: `{user_id}`',
                parse_mode='MarkdownV2'
            )
        
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard = [
                [InlineKeyboardButton("🦅 Get Started", callback_data="Enter")],
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase")],
                [
                    InlineKeyboardButton("⚙️ Tools & Commands", callback_data="Commands"),
                    InlineKeyboardButton("📚 How It Works", callback_data="Features")
                ],
                [
                    InlineKeyboardButton("🛠 Support Team", url=admin_link),
                    InlineKeyboardButton("🌍 Join Community", callback_data="community")
                ],
                [InlineKeyboardButton("👤 Account Details", callback_data="profile")]
            ]

            await update.message.reply_photo(
                logo,
                caption=fr"""🦅 *AORUS OTP — The Ultimate Spoofing Experience*

Since 2022\, AORUS OTP has been at the forefront of Telegram\-based OTP spoofing — delivering elite\-grade AI voice calls\, ultra\-fast global routes\, and unmatched spoofing precision\.

Trusted by thousands\, AORUS OTP combines *military\-grade stealth*\, *automated real\-time controls*\, and *cutting\-edge voice AI*\, making it the *most stable and advanced OTP grabbing system* in the scene\.

Whether you're verifying accounts\, automating workflows — AORUS equips you with the tools to *outpace*\, *outsmart*\, *and outperform*\.

🧠 *Built to Spoof\. Powered by Stability*\.
🤖 AI\-Powered Voice Delivery
🟢 Global Coverage – 24/7 Uptime
🛡 Military\-Grade Spoofing Stealth
🖥 Fully Automated\, Real\-Time Controls
⚡️ Blazing\-Fast Execution – No Delays

💬 Welcome, *{escape_markdown(name)}* — you're now backed by the best\.""",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MarkdownV2'
            )
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

#CHECK FOR PHONELIST
async def phonelist(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') != 'CS':
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                keyboard = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
                ]
                await update.message.reply_text(spoof_message, parse_mode='MarkdownV2', 
                                              reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                keyboard = [
                    [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                     InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
                ]
                await update.message.reply_text(
                    "⚠️ Access Denied: This command is available to subscribed users only.\nUpgrade your plan to continue.",
                    reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")


async def run_call_process(user_id, args, update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    if len(args) < 6:
        await update.message.reply_text(
            fr"""❌ *Invalid Command Format*  
To initiate a spoofing call, please provide all 5 required arguments:

`{args[0]} [victim_number] [spoof_number] [victim_name] [service_name] [digit_length]`

🔹 *Example*:  
`{args[0]} +1234567890 +0987654321 John PayPal 6`""",
            parse_mode='MarkdownV2')
    else:
        if args[0] == '/call':
            script = 'Disabled'
        else:
            script = 'Enabled'
        
        victim_number, spoof_number, victim_name, service_name, otp_digit = args[1], args[2], args[3], args[4], args[5]
        
        if (is_valid_phone_number(victim_number) and victim_number not in spoofing_numbers) and \
           (is_valid_phone_number(spoof_number) and check_spoof(spoof_number, service_name, victim_name, spoofing_numbers) == True) and \
           (is_name_valid(victim_name) == True) and check_otp_len(otp_digit) == True:
            
            ringing = [[InlineKeyboardButton("End Call", callback_data="endcall")]]
            set_user_value(user_id, 'In_Call', True)
            set_user_value(user_id, 'Last_Call', str(args))
            
            await update.message.reply_text(
                fr"""🟢 *CALL DETAILS *
📞 *VICTIM NUMBER*: `{escape_markdown(victim_number)}`
☎ *CALLER ID*: `{escape_markdown(spoof_number)}`
🏦 *SERVICE NAME*: `{escape_markdown(get_service_name(service_name))}`
🚹 *VICTIM NAME* : `{victim_name}`
💬 *CUSTOM SCRIPT* : `{script}`
🎙 *VOICE* : `{get_user_info(user_id, 'Voice')}`
🗣 *ACCENT* : `{get_user_info(user_id, 'Accent')}`
🔢 *OTP DIGITS*: `{otp_digit}`""",
                parse_mode='MarkdownV2')
            
            sleep(0.5)
            await update.message.reply_text(r"✅ *CALL STARTED*\.\.\.", parse_mode='MarkdownV2')
            await asyncio.sleep(randint(1, 2))
            await update.message.reply_text(r"📞 *CALL RINGING*", 
                                          reply_markup=InlineKeyboardMarkup(ringing),
                                          parse_mode='MarkdownV2')
            await asyncio.sleep(randint(2, 3))
            await update.message.reply_text(r"❌ *CALL CANCELED*", parse_mode='MarkdownV2')
            await asyncio.sleep(0.2)
            
            if get_user_info(user_id, 'In_Call'):
                ran_num = get_user_info(user_id, 'Err_Num')
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url=errors_links[ran_num])]
                ]
                await update.message.reply_text(text=errors[ran_num], 
                                              reply_markup=InlineKeyboardMarkup(error))
            
            set_user_value(user_id, 'In_Call', False)
        
        elif not is_valid_phone_number(victim_number):
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/5')]
            ]
            await update.message.reply_text(
                "❌ Invalid victim phone number format. Please enter a valid number including country code.",
                reply_markup=InlineKeyboardMarkup(error))
        
        elif victim_number in spoofing_numbers:
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/10')]
            ]
            await update.message.reply_text(
                "❌ This number is in the spoofing list. Please choose a different one.",
                reply_markup=InlineKeyboardMarkup(error))
        
        elif check_spoof(spoof_number, service_name, victim_name, spoofing_numbers) != True:
            if check_spoof(spoof_number, service_name, victim_name, spoofing_numbers) == 'Not Found':
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/6')]
                ]
                await update.message.reply_text(
                    "❌ Phone number not found. Please check the spoof list and try again.",
                    reply_markup=InlineKeyboardMarkup(error))
            
            elif check_spoof(spoof_number, service_name, victim_name, spoofing_numbers) == 'Found':
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/11')]
                ]
                await update.message.reply_text(
                    f"❌ Not a VIP Spoof Number. This number for {get_service_name_bynum(spoof_number)} spoof.",
                    reply_markup=InlineKeyboardMarkup(error))
            
            elif check_spoof(spoof_number, service_name, victim_name, spoofing_numbers) == 'Name Found':
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/12')]
                ]
                await update.message.reply_text(
                    "❌ Name Conflicts with a Service Name. Names can't be a service name.",
                    reply_markup=InlineKeyboardMarkup(error))
            
            elif check_spoof(spoof_number, service_name, victim_name, spoofing_numbers) == False:
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/7')]
                ]
                await update.message.reply_text(
                    "❌ Spoof number and service do not match. Please verify your inputs.",
                    reply_markup=InlineKeyboardMarkup(error))
        
        elif not is_name_valid(victim_name):
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/8')]
            ]
            await update.message.reply_text(
                "❌ Invalid name format. Names should only contain lower and upper case letters.",
                reply_markup=InlineKeyboardMarkup(error))
        
        elif not check_otp_len(otp_digit):
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/9')]
            ]
            await update.message.reply_text(
                "❌ Invalid OTP length. Please enter between 4 and 8 digits.",
                reply_markup=InlineKeyboardMarkup(error))
        
        elif check_otp_len(otp_digit) == 'Null':
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/13')]
            ]
            await update.message.reply_text(
                "❌ Invalid OTP type. Please enter digits not text.",
                reply_markup=InlineKeyboardMarkup(error))


async def run_precall_process(user_id, args, update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    if len(args) < 4:
        await update.message.reply_text(
            fr"""❌ *Invalid Command Format*  
To initiate a spoofing call, please provide all 3 required arguments:

`{args[0]} [victim_number] [victim_name] [digit_length]`

🔹 *Example*:  
`{args[0]} +1234567890 John 6`""",
            parse_mode='MarkdownV2')
    else:
        victim_number, victim_name, otp_digit = args[1], args[2], args[3]
        
        if (is_valid_phone_number(victim_number) and victim_number not in spoofing_numbers) and \
           (is_name_valid(victim_name) == True) and check_otp_len(otp_digit) == True:
            
            ringing = [[InlineKeyboardButton("End Call", callback_data="endcall")]]
            set_user_value(user_id, 'Last_Call', str(args))
            set_user_value(user_id, 'In_Call', True)
            
            await update.message.reply_text(
                fr"""🟢 *CALL DETAILS* 
📞 *VICTIM NUMBER*: `{escape_markdown(victim_number)}`
☎ *CALLER ID*: `{escape_markdown(get_spoof_number(args[0][1:]))}`
🏦 *SERVICE NAME*: `{escape_markdown(get_service_name(args[0][1:]))}`
🚹 *VICTIM NAME* : `{victim_name}`
🎙 *VOICE* : `{get_user_info(user_id, 'Voice')}`
🗣 *ACCENT* : `{get_user_info(user_id, 'Accent')}`
🔢 *OTP DIGITS*: `{otp_digit}`""",
                parse_mode='MarkdownV2')
            
            await asyncio.sleep(0.5)
            await update.message.reply_text(r"✅ *CALL STARTED*\.\.\.", parse_mode='MarkdownV2')
            await asyncio.sleep(randint(1, 2))
            await update.message.reply_text(r"📞 *CALL RINGING*", 
                                          reply_markup=InlineKeyboardMarkup(ringing),
                                          parse_mode='MarkdownV2')
            await asyncio.sleep(randint(2, 3))
            await update.message.reply_text(r"❌ *CALL CANCELED*", parse_mode='MarkdownV2')
            await asyncio.sleep(0.2)
            
            if get_user_info(user_id, 'In_Call'):
                ran_num = get_user_info(user_id, 'Err_Num')
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url=errors_links[ran_num])]
                ]
                await update.message.reply_text(text=errors[ran_num], 
                                              reply_markup=InlineKeyboardMarkup(error))
            
            set_user_value(user_id, 'In_Call', False)
        
        elif not is_valid_phone_number(victim_number):
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/5')]
            ]
            await update.message.reply_text(
                "❌ Invalid victim phone number format. Please enter a valid number including country code.",
                reply_markup=InlineKeyboardMarkup(error))
        
        elif victim_number in spoofing_numbers:
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/10')]
            ]
            await update.message.reply_text(
                "❌ This number is in the spoofing list. Please choose a different one.",
                reply_markup=InlineKeyboardMarkup(error))
        
        elif not is_name_valid(victim_name):
            if is_name_valid(victim_name) == False:
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/8')]
                ]
                await update.message.reply_text(
                    "❌ Invalid name format. Names should only contain lower and upper case letters.",
                    reply_markup=InlineKeyboardMarkup(error))
            else:
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/12')]
                ]
                await update.message.reply_text(
                    "❌ ERROR: Name Conflicts with a Service Name. Names can't be a service name.",
                    reply_markup=InlineKeyboardMarkup(error))
        
        elif not (4 <= int(otp_digit) <= 8):
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/9')]
            ]
            await update.message.reply_text(
                "❌ Invalid OTP length. Please enter between 4 and 8 digits.",
                reply_markup=InlineKeyboardMarkup(error))
        
        elif check_otp_len(otp_digit) == 'Null':
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/13')]
            ]
            await update.message.reply_text(
                "❌ Invalid OTP type. Please enter digits not text.",
                reply_markup=InlineKeyboardMarkup(error))

#PROFILE
async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            expiry_date = get_user_info(user_id, 'Expiry_Date')
            if not check_subscription(expiry_date):
                plan = 'Free'
                status = '🔴 Not Active'
                date = 'N/A'
            else:
                plan = 'Pro'
                status = '🟢 Active'
                date = get_user_info(user_id, 'Expiry_Date')[0:16]
            
            keyboard = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
            ]
            
            await update.message.reply_text(
                fr"""👤 *Your Profile Details*

🆔 *User ID*: `{user_id}`
📛 *Username*: `{escape_markdown(get_user_info(user_id, 'Username_Name'))}`
⭐️ *Status*: `{status}`
📦 *Plan*: `{plan}`
⏳ *Plan End in*: `{escape_markdown(date)}`""",
                parse_mode='MarkdownV2',
                reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

#REDEEM KEY
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            if not context.args:
                await update.message.reply_text(
                    r"""❌ *Activation Key Missing*  
To proceed, please enter your key using:  
`/redeem [activation key]`""",
                    parse_mode="MarkdownV2")
            else:
                key = context.args[0]
                msg = redeem_keys(user_id, key)
                await update.message.reply_text(text=msg, parse_mode='MarkdownV2')
                
                if msg[0] == '✅':
                    parts = key.split("-")
                    duration_code = parts[1]
                    duration_text = duration(duration_code)
                    await context.bot.send_message(
                        chat_id=redeem_keys,
                        text=fr'*Key For {duration_text}*\n'
                             fr'*Redeemed by*: {escape_markdown(get_user_info(user_id, "User_Name"))}\n'
                             fr'*Name*: `{escape_markdown(get_user_info(user_id, "First_Name"))}`\n'
                             fr'*Chat Id: *`{user_id}`',
                        parse_mode='MarkdownV2')
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def set_voice(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                keyboard = [
                    [InlineKeyboardButton("🎙 Change Voice", callback_data="setvoice"),
                     InlineKeyboardButton("🗣 Change Accent", callback_data="setaccent")],
                    [InlineKeyboardButton("🔙 Leave it As is", callback_data="back1")]
                ]
                
                current_voice = get_user_info(user_id, 'Voice')
                current_accent = get_user_info(user_id, 'Accent')
                gender = 'Male' if current_voice in ['Jorch', 'William'] else 'Female'
                
                await update.message.reply_text(
                    fr"""🎙 *Current Voice Configuration*
🚹 *Voice Name*: `{current_voice}`
⚥ *Gender*: `{gender}`
🗣 *Accent*: `{current_accent}`

To select a different voice, please choose one from the list below\.
For a full list of available voices, use the command: /VoiceList

🛠 Customize your voice to match your needs and enhance the experience\.""",
                    parse_mode='MarkdownV2',
                    reply_markup=InlineKeyboardMarkup(keyboard))
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await update.message.reply_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            else:
                await update.message.reply_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def chose_voice_accent(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, "Banned"):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                if query.data == 'setvoice':
                    keyboard = [
                        [InlineKeyboardButton("🚹 Jorch", callback_data="Jorch"),
                         InlineKeyboardButton("🚹 William", callback_data="William")],
                        [InlineKeyboardButton("🚺 Emma", callback_data="Emma"),
                         InlineKeyboardButton("🚺 Lara", callback_data="Lara")],
                        [InlineKeyboardButton("🔙 Leave it As is", callback_data="back1")]
                    ]
                    await query.edit_message_text(
                        "🗣 Please select one of the voices below.",
                        reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    keyboard = [
                        [InlineKeyboardButton("🇺🇸 North America", callback_data="North America"),
                         InlineKeyboardButton("🇬🇧 Europe", callback_data="Europe")],
                        [InlineKeyboardButton("🇲🇽 Latin America", callback_data="Latin America"),
                         InlineKeyboardButton("🌏 Asia & Pacific", callback_data="Asia & Pacific")],
                        [InlineKeyboardButton("🌍 Middle East & Africa", callback_data="Middle East & Africa")],
                        [InlineKeyboardButton("🔙 Leave it As is", callback_data="back1")]
                    ]
                    await query.edit_message_text(
                        "🗣 Please select one of the accents below.",
                        reply_markup=InlineKeyboardMarkup(keyboard))
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await query.edit_message_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            else:
                await query.edit_message_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.edit_message_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.edit_message_text("❌ You can't use buttons while making a custom script.")

async def choose_voice(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, "Banned"):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                voice = query.data
                set_user_value(user_id, "Voice", voice)
                keyboard = [[InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]]
                await query.edit_message_text(
                    f"✅ Voice changed to {voice} successfully!",
                    reply_markup=InlineKeyboardMarkup(keyboard))
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await query.edit_message_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            else:
                await query.edit_message_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.edit_message_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.edit_message_text("❌ You can't use buttons while making a custom script.")

async def choose_accent(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, "Banned"):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                accent = query.data
                set_user_value(user_id, "Accent", accent)
                keyboard = [[InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]]
                await query.edit_message_text(
                    f"✅ Accent changed to {accent} successfully!",
                    reply_markup=InlineKeyboardMarkup(keyboard))
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await query.edit_message_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            else:
                await query.edit_message_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.edit_message_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.edit_message_text("❌ You can't use buttons while making a custom script.")

async def caal_cuscaal(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')) and \
               check_subscription(get_user_info(user_id, 'Expiry_Date')) != 'Null':
                
                args = update.message.text.split(maxsplit=5)
                await run_call_process(user_id, args, update, context)
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await update.message.reply_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            
            elif get_user_info(user_id, 'Expiry_Date') == 'N/A':
                await update.message.reply_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def recall(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                s = get_user_info(user_id, 'Last_Call')
                if s == 'N/A':
                    await update.message.reply_text("⚠️ No saved call found. Please use /call first.")
                else:
                    args = ast.literal_eval(s)
                    if len(args) == 6:
                        await run_call_process(user_id, args, update, context)
                    else:
                        await run_precall_process(user_id, args, update, context)
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await update.message.reply_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            
            elif get_user_info(user_id, 'Expiry_Date') == 'N/A':
                await update.message.reply_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def voicelist(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                back_button = [[InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back4")]]
                await update.message.reply_audio(Jorch, caption='🚹 Jorch')
                await update.message.reply_audio(William, caption='🚹 William')
                await update.message.reply_audio(Emma, caption='🚺 Emma')
                await update.message.reply_audio(Lara, caption='🚺 Lara', 
                                               reply_markup=InlineKeyboardMarkup(back_button))
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await update.message.reply_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            else:
                await update.message.reply_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def prenuilt_call(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')) and \
               check_subscription(get_user_info(user_id, 'Expiry_Date')) != 'Null':
                
                args = update.message.text.split(maxsplit=3)
                await run_precall_process(user_id, args, update, context)
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await update.message.reply_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            
            elif get_user_info(user_id, 'Expiry_Date') == 'N/A':
                await update.message.reply_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, "Banned"):
        if get_user_info(user_id, 'In_Action') == 'NN':
            command = query.data
            count = int(command[-1])
            
            # In PTB, we can't directly delete multiple messages like this
            # You might need to track message IDs to delete them
            # For now, we'll just edit the current message
            message_id = query.message.message_id
            keyboard = [
                [InlineKeyboardButton("🦅 Get Started", callback_data="Enter")],
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase")],
                [
                    InlineKeyboardButton("⚙️ Tools & Commands", callback_data="Commands"),
                    InlineKeyboardButton("📚 How It Works", callback_data="Features")
                ],
                [
                    InlineKeyboardButton("🛠 Support Team", url=admin_link),
                    InlineKeyboardButton("🌍 Join Community", callback_data="community")
                ],
                [InlineKeyboardButton("👤 Account Details", callback_data="profile")]
            ]
            if query.data=='back4':
                await context.bot.delete_message(chat_id=user_id, message_id=message_id-1)
                await context.bot.delete_message(chat_id=user_id, message_id=message_id-2)
                await context.bot.delete_message(chat_id=user_id, message_id=message_id-3)
            await query.message.delete()
            await query.message.reply_photo(
                logo,
                caption=fr"""🦅 *AORUS OTP — The Ultimate Spoofing Experience*

Since 2022\, AORUS OTP has been at the forefront of Telegram\-based OTP spoofing — delivering elite\-grade AI voice calls\, ultra\-fast global routes\, and unmatched spoofing precision\.

Trusted by thousands\, AORUS OTP combines *military\-grade stealth*\, *automated real\-time controls*\, and *cutting\-edge voice AI*\, making it the *most stable and advanced OTP grabbing system* in the scene\.

Whether you're verifying accounts\, automating workflows — AORUS equips you with the tools to *outpace*\, *outsmart*\, *and outperform*\.

🧠 *Built to Spoof\. Powered by Stability*\.
🤖 AI\-Powered Voice Delivery
🟢 Global Coverage – 24/7 Uptime
🛡 Military\-Grade Spoofing Stealth
🖥 Fully Automated\, Real\-Time Controls
⚡️ Blazing\-Fast Execution – No Delays

💬 Welcome, *{escape_markdown(get_user_info(user_id,'First_Name'))}* — you're now backed by the best\.""",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MarkdownV2'
            )
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while making a custom script.")

async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard = [[InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]]
            await query.delete_message()
            await query.message.reply_text(
                r"""🦅 *AORUS OTP* \- Commands
❓ *Commands*
    • /redeem    ➜ Redeem a Key
    • /phonelist ➜ Latest Spoof Numbers
    • /plan      ➜ Account Status
    • /help      ➜ Commands List                         
    • /purchase  ➜ Purchase Access
                                                                                
⚙️ *Call modules*
    • /call       ➜ OTP for any service                                                              
    • /paypal     ➜ Paypal OTP
    • /venmo      ➜ Venmo OTP
    • /applepay   ➜ ApplePay OTP
    • /coinbase   ➜ Coinbase OTP
    • /microsoft  ➜ Microsoft OTP
    • /amazon     ➜ Amazon OTP
    • /quadpay    ➜ Quadpay OTP
    • /cashapp    ➜ Cashapp OTP                               
    • /citizens   ➜ Citizens OTP 
    • /marcus     ➜ Marcus OTP
    • /creditcard ➜ CreditCard OTP
    • /carrier    ➜ Carrier OTP 
                                                                                                                                                                            
👤 *Custom commands*
    • /setscript  ➜ Create Custom Script
    • /script     ➜ Check Your Script 
    • /customcall ➜ Custom Script Call     
    • /setvoice   ➜ Set a Voice For Call
    • /voicelist  ➜ Check Voices List
    • /recall     ➜ Recall victim""",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MarkdownV2')
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while making a custom script.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard = [[InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]]
            await update.message.reply_text(
                r"""🦅 *AORUS OTP* \- Commands
❓ *Commands*
    • /redeem    ➜ Redeem a Key
    • /phonelist ➜ Latest Spoof Numbers
    • /plan      ➜ Account Status
    • /help      ➜ Commands List                         
    • /purchase  ➜ Purchase Access
                                                                                
⚙️ *Call modules*
    • /call       ➜ OTP for any service                                                              
    • /paypal     ➜ Paypal OTP
    • /venmo      ➜ Venmo OTP
    • /applepay   ➜ ApplePay OTP
    • /coinbase   ➜ Coinbase OTP
    • /microsoft  ➜ Microsoft OTP
    • /amazon     ➜ Amazon OTP
    • /quadpay    ➜ Quadpay OTP
    • /cashapp    ➜ Cashapp OTP                               
    • /citizens   ➜ Citizens OTP 
    • /marcus     ➜ Marcus OTP
    • /creditcard ➜ CreditCard OTP
    • /carrier    ➜ Carrier OTP 
                                                                                                                                                                            
👤 *Custom commands*
    • /setscript  ➜ Create Custom Script
    • /script     ➜ Check Your Script 
    • /customcall ➜ Custom Script Call     
    • /setvoice   ➜ Set a Voice For Call
    • /voicelist  ➜ Check Voices List
    • /recall     ➜ Recall victim""",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MarkdownV2')
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            expiry_date = get_user_info(user_id, 'Expiry_Date')
            if not check_subscription(expiry_date):
                plan = 'Free'
                status = '🔴 Not Active'
                date = 'N/A'
            else:
                plan = 'Pro'
                status = '🟢 Active'
                date = get_user_info(user_id, 'Expiry_Date')[0:16]
            
            keyboard = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
            ]
            await query.delete_message()
            await query.message.reply_text(
                fr"""👤 *Your Profile Details*

🆔 *User ID*: `{user_id}`
📛 *Username*: `{escape_markdown(get_user_info(user_id, 'Username_Name'))}`
⭐️ *Status*: `{status}`
📦 *Plan*: `{plan}`
⏳ *Plan End in*: `{escape_markdown(date)}`""",
                parse_mode='MarkdownV2',
                reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while making a custom script.")

async def features(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
            ]
            await query.delete_message()
            await query.message.reply_text(
                r"""🦅 *AORUS OTP*

❓ Here you can find frequently asked questions that we have compiled for you in an organized and user\-friendly manner\. They'll be updated as we go\!

ℹ️ OTP Phishing is when you make a call pretending to be from a certain company requesting for OTP Code sent to the device\. For example, if you tried to login into an account protected by OTP, you could make the call pretending to be the service itself requesting the OTP Code for Account Security Purposes and it will get sent back to you\.

💬 If you can't find the answer you're looking for, feel free to reach out to our support team\. Warm regards, Support\.""",
                parse_mode='MarkdownV2',
                reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while making a custom script.")

async def community(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard = [
                [
                    InlineKeyboardButton("📢 Main Channel", url=main_channel_link),
                    InlineKeyboardButton("✅ Vouches Channel", url=vouches_link)
                ],
                [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
            ]
            
            await query.edit_message_media(
                media=InputMediaPhoto(logo,
                caption=r"""Welcome to *AORUS OTP*\! 🚀 
Stay connected with our Telegram channels for the latest updates\, exclusive features\, and real\-time support\. 
Whether you're here for fast OTP services or want to stay informed about new tools and improvements\, our channels have you covered\.
Join us and be part of the growing *AORUS OTP community*\!""",
                parse_mode='MarkdownV2'),
                reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while making a custom script.")

async def purchase_menu(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query if hasattr(update, 'callback_query') else None
    user_id = update.effective_user.id
    
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard = [
                [InlineKeyboardButton("⚡ 1 Day 30$", callback_data="30")],
                [InlineKeyboardButton("⏱️ 3 Days 55$", callback_data="55")],
                [InlineKeyboardButton("🗓️ 1 Week 95$", callback_data="95")],
                [InlineKeyboardButton("📅 1 Month 210$", callback_data="210")],
                [InlineKeyboardButton("📱 Spoof Number 20$", callback_data="20")],
                [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
            ]
            
            if query:
                await query.edit_message_media(
                    media=InputMediaPhoto(logo2,
                    caption="💸 Choose your subscription type:"),
                    reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await update.message.reply_photo(
                    logo2,
                    caption="💸 Choose your subscription type:",
                    reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            if query:
                await query.delete_message()
                await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
            else:
                await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            if query:
                await query.delete_message()
                await query.message.reply_text("❌ You can't use buttons while making a custom script.")
            else:
                await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def enter_menu(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                enter_buttons = [
                    [
                        InlineKeyboardButton("⚙️ Aorus Tools", callback_data="Commands"),
                        InlineKeyboardButton("📞 Start Call", callback_data="startcall")
                    ],
                    [InlineKeyboardButton("📘 How It Works ", callback_data="Features")],
                    [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]
                ]
                await query.delete_message()
                await query.message.reply_text(
                    fr"""🎉 *Welcome, {escape_markdown(get_user_info(user_id, 'First_Name'))}\!*

You're now an *active subscriber* of **AORUS OTP** — the most advanced Telegram spoofing suite\.

🔐 Your access has been verified\.

*Here's what you can do*:
📞 *Spoof Voice Call* — launch a real\-time AI call
⚙️ *Use Tools* — modules & features
📘 *How It Works* — step\-by\-step guide

You're all set\. 👇 Choose an option below to begin\.""",
                    parse_mode='MarkdownV2',
                    reply_markup=InlineKeyboardMarkup(enter_buttons))
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await query.edit_message_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            else:
                await query.edit_message_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while making a custom script.")

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            amount = query.data
            btc, usdt, eth, ltc, sol = f'btc+{amount}', f'usdt+{amount}', f'eth+{amount}', f'ltc+{amount}', f'sol+{amount}'
            
            keyboard = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link)],
                [InlineKeyboardButton("₿ BTC", callback_data=btc)],
                [
                    InlineKeyboardButton("💲 USDT", callback_data=usdt),
                    InlineKeyboardButton("♢ ETH", callback_data=eth)
                ],
                [
                    InlineKeyboardButton("𝑳 LTC", callback_data=ltc),
                    InlineKeyboardButton("◎ SOL", callback_data=sol)
                ],
                [InlineKeyboardButton("🔙 BACK TO PRICES", callback_data='Purchase')]
            ]
            
            await query.edit_message_media(
                media=InputMediaPhoto(crypto,
                caption="""💸Please choose one of the following wallets below:
ℹ For other wallet please contact Support."""),
                reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while making a custom script.")

async def wallet_info(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            com = query.data
            symbol = com[:com.find('+')]
            amount = com[com.find('+')+1:]
            
            keyboard = [
                [
                    InlineKeyboardButton("🛠 Support Team", url=admin_link),
                    InlineKeyboardButton("🔙 BACK TO PRICING MENU", callback_data="Purchase")
                ]
            ]
            await query.message.delete()
            await query.message.chat.send_message(
                get_wallet_message(symbol, int(amount)),
                parse_mode='MarkdownV2',
                reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while configuring your first call.")
        else:
            await query.delete_message()
            await query.message.reply_text("❌ You can't use buttons while making a custom script.")

async def setscript(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                set_user_value(user_id, 'In_Action', 'CS')
                await update.message.reply_text(
                    r"""💬 *Step 1 of 3*: Please enter the first part of your script\.
This is the message the user will hear first\.

📝 *Example*:
Hello `{name}`, we've noticed unusual activity on your `{service}` account\. If this wasn't you, please press 1\.

📌 *Available Variables*:
`{name}` – the recipient's name
`{service}` – the platform or service name
`{otpdigits}` – the code or digits you want to insert""",
                    parse_mode="MarkdownV2")
                
                return STEP1
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await update.message.reply_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            
            elif get_user_info(user_id, 'Expiry_Date') == 'N/A':
                await update.message.reply_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
    
    return ConversationHandler.END

async def resetscript(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == "NN":
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                set_user_value(user_id, 'Custom_Script', 'N/A')
                await update.message.reply_text("✅ Custom script reset successfully!")
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await update.message.reply_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            
            elif get_user_info(user_id, 'Expiry_Date') == 'N/A':
                await update.message.reply_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def step1(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        context.user_data['step1'] = update.message.text
        await update.message.reply_text(
            r"""💬 *Step 2 of 3*: Please enter the second part of your script\.
This follows the user's response from the first message\.

📝 *Example*:
To block this request, please enter the `{otpdigits}`\-digit security code we just sent\.

📌 *Available Variables*:
`{name}` – the recipient's name
`{service}` – the platform or service name
`{otpdigits}` – the security code or number of digits""",
            parse_mode='MarkdownV2')
        
        return STEP2
    
    return ConversationHandler.END

async def step2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        context.user_data['step2'] = update.message.text
        await update.message.reply_text(
            r"""💬 *Step 3 of 3*: Please enter the final part of your script\.
This message is played after the user enters the security code\.

📝 *Example*:
The code you provided is valid\. The request has been successfully blocked\.

📌 Available Variables:
`{name}` – the recipient's name
`{service}` – the platform or service name
`{otpdigits}` – the entered security code""",
            parse_mode="MarkdownV2")
        
        return STEP3
    
    return ConversationHandler.END

async def step3(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        set_user_value(user_id, 'In_Action', 'NN')
        context.user_data['step3'] = update.message.text
        
        script = fr"*1\)*\n {escape_markdown(context.user_data['step1'])}\n\n*2\)*\n {escape_markdown(context.user_data['step2'])}\n\n*3\)*\n {escape_markdown(context.user_data['step3'])}"
        set_user_value(user_id, 'Custom_Script', script)
        
        keyboard = [[InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]]
        await update.message.reply_text(
            "✅ Script Created Successfully!\nUse /script To check your Custom Script.",
            reply_markup=InlineKeyboardMarkup(keyboard))
    
    return ConversationHandler.END

async def spoof_button_clicked(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            if get_user_info(user_id, 'First_Call') == 'N/A':
                set_user_value(user_id, 'In_Action', 'FC')
                keyboard1 = [
                    [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                     InlineKeyboardButton("🛠 Support Team", url=admin_link)]
                ]
                
                if check_subscription(get_user_info(user_id, 'Expiry_Date')):
                    await query.edit_message_text(
                        r"📞 *1 Of 5*:\n\nIn this step you have to enter the victim number and you must provide a valid phone number and the victim number must be non spoof number in the system\.\nPlease enter the victim's phone number \(include country code\):",
                        parse_mode='MarkdownV2')
                    
                    return VICTIM_NUMBER
                
                elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                    await query.edit_message_text(
                        "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                        reply_markup=InlineKeyboardMarkup(keyboard1))
                
                elif get_user_info(user_id, 'Expiry_Date') == 'N/A':
                    await query.edit_message_text(
                        "🚫 No active subscription found.\nPlease activate a key to get started.",
                        reply_markup=InlineKeyboardMarkup(keyboard1))
            
            else:
                await query.edit_message_text(
                    fr"⚠ You Already made your first call\.\n `{escape_markdown(get_user_info(user_id, 'First_Call'))}`",
                    parse_mode='MarkdownV2')
        
        elif get_user_info(user_id, 'In_Action') == 'CS':
            await query.edit_message_text("❌ You can't use buttons while making a custom script.")
    
    return ConversationHandler.END

async def get_victim_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        victim_number = update.message.text
        
        if not is_valid_phone_number(victim_number) or victim_number in spoofing_numbers:
            if not is_valid_phone_number(victim_number):
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/5')]
                ]
                await update.message.reply_text(
                    "❌ Invalid victim phone number format. Please enter a valid number including country code.",
                    reply_markup=InlineKeyboardMarkup(error))
                return VICTIM_NUMBER
            
            else:
                error = [
                    [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                     InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/10')]
                ]
                await update.message.reply_text(
                    "❌ This number is in the spoofing list. Please choose a different one.",
                    reply_markup=InlineKeyboardMarkup(error))
                return VICTIM_NUMBER
        
        context.user_data['victim_number'] = victim_number
        await update.message.reply_text(
            r"📞 *2 Of 5*:\n\nIn this step you have to enter one of our spoof numbers and you must provide a valid and existing phone number in the spoof system\.\nPlease enter the spoof phone number, use /phonelist to check spoof list:",
            parse_mode='MarkdownV2')
        
        return SPOOF_NUMBER
    
    return ConversationHandler.END

async def get_spoof_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if not is_valid_phone_number(update.message.text):
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/5')]
            ]
            await update.message.reply_text(
                "❌ Invalid spoof phone number format. Please enter a valid number including country code.",
                reply_markup=InlineKeyboardMarkup(error))
            return SPOOF_NUMBER
        
        elif update.message.text not in spoofing_numbers:
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/6')]
            ]
            await update.message.reply_text(
                "❌ Phone number not found. Please check the spoof list and try again.",
                reply_markup=InlineKeyboardMarkup(error))
            return SPOOF_NUMBER
        
        context.user_data['spoof_number'] = update.message.text
        await update.message.reply_text(
            r"📞 *3 Of 5*:\n\nIn this step you have to enter the victim name this is the name who the bot will use when make the call and this name must contain only characters and not exist in services name, use /phonelist to check spoof list\.\nPlease enter the victim name:",
            parse_mode='MarkdownV2')
        
        return VICTIM_NAME
    
    return ConversationHandler.END

async def get_victim_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if not update.message.text.isalpha():
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/8')]
            ]
            await update.message.reply_text(
                "❌ Invalid name format. Names should only contain lower and upper case letters.",
                reply_markup=InlineKeyboardMarkup(error))
            return VICTIM_NAME
        
        elif update.message.text.upper() in spoofing_services:
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/12')]
            ]
            await update.message.reply_text(
                "❌ Name Conflicts with a Service Name. Names can't be a service name.",
                reply_markup=InlineKeyboardMarkup(error))
            return VICTIM_NAME
        
        context.user_data['victim_name'] = update.message.text
        spoof_number = context.user_data['spoof_number']
        
        await update.message.reply_text(
            fr"📞 *4 Of 5*:\n\nIn this step you have to enter the service or the company name and the service name related by the spoof number per example you choose the `{escape_markdown(spoof_number)}` then the service name will be `{get_service_name_bynum(spoof_number)}`\.",
            parse_mode='MarkdownV2')
        
        context.user_data['service_name'] = get_service_name_bynum(spoof_number)
        await update.message.reply_text(
            r"📞 *5 Of 5*:\n\nIn this step you have to enter the otp length it must be between 4 and 8 and digits not text\.",
            parse_mode='MarkdownV2')
        
        return OTP_DIGIT
    
    return ConversationHandler.END

async def get_otp_digit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if not check_otp_len(update.message.text):
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/9')]
            ]
            await update.message.reply_text(
                "❌ Invalid OTP length. Please enter between 4 and 8 digits.",
                reply_markup=InlineKeyboardMarkup(error))
            return OTP_DIGIT
        
        elif check_otp_len(update.message.text) == 'Null':
            error = [
                [InlineKeyboardButton("🛠 Support Team", url=admin_link),
                 InlineKeyboardButton("ℹ️ More Info", url='https://t.me/repports_errors/13')]
            ]
            await update.message.reply_text(
                "❌ Invalid OTP type. Please enter digits not text.",
                reply_markup=InlineKeyboardMarkup(error))
            return OTP_DIGIT
        
        context.user_data['otp_digit'] = update.message.text
        data = context.user_data
        cmd = fr"`/call {escape_markdown(data['victim_number'])} {escape_markdown(data['spoof_number'])} {data['victim_name']} {data['service_name']} {data['otp_digit']}`"
        await update.message.reply_text(
            fr"""✅ *Spoof Call Configured:*
Copy this command and use it to make your first call:

{cmd}""",
            parse_mode="MarkdownV2")
        
        set_user_value(user_id, 'In_Action', 'NN')
        set_user_value(user_id, 'First_Call', )
    
    return ConversationHandler.END

async def script_info(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        if get_user_info(user_id, 'In_Action') == 'NN':
            keyboard1 = [
                [InlineKeyboardButton("💰 Plans & Pricing", callback_data="Purchase"),
                 InlineKeyboardButton("🛠 Support Team", url=admin_link)]
            ]
            
            if check_subscription(get_user_info(user_id, 'Expiry_Date')) and \
               check_subscription(get_user_info(user_id, 'Expiry_Date')) != 'Null':
                
                if get_user_info(user_id, "Custom_Script") != 'N/A':
                    keyboard = [[InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back1")]]
                    await update.message.reply_text(
                        fr"💬 *Your Custom Script is*:\n{get_user_info(user_id, 'Custom_Script')}",
                        parse_mode="MarkdownV2",
                        reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    await update.message.reply_text(
                        "❌ You don't have a custom script, use /setscript to make one.")
            
            elif not check_subscription(get_user_info(user_id, 'Expiry_Date')):
                await update.message.reply_text(
                    "❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
            
            elif get_user_info(user_id, 'Expiry_Date') == 'N/A':
                await update.message.reply_text(
                    "🚫 No active subscription found.\nPlease activate a key to get started.",
                    reply_markup=InlineKeyboardMarkup(keyboard1))
        
        elif get_user_info(user_id, 'In_Action') == 'FC':
            await update.message.reply_text("❌ You can't use commands while configuring your first call.")
        else:
            await update.message.reply_text("❌ You can't use commands while making a custom script.")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        keyboard = [[InlineKeyboardButton("🛠 Support Team", url=admin_link)]]
        await update.message.reply_text(
            "⚠️ Unrecognized command. Please contact support if you need assistance.",
            reply_markup=InlineKeyboardMarkup(keyboard))

async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE): #DONE
    user_id = update.effective_user.id
    if not get_user_info(user_id, 'Banned'):
        keyboard = [[InlineKeyboardButton("🛠 Support Team", url=admin_link)]]
        await update.message.reply_text(
            """🤖 Sorry, I couldn't process your request.
For further assistance, please contact our support team.""",
            reply_markup=InlineKeyboardMarkup(keyboard))

# Conversation handlers
script_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("setscript", setscript)],
    states={
        STEP1: [MessageHandler(filters.TEXT & ~filters.COMMAND, step1)],
        STEP2: [MessageHandler(filters.TEXT & ~filters.COMMAND, step2)],
        STEP3: [MessageHandler(filters.TEXT & ~filters.COMMAND, step3)]
    },
    fallbacks=[CommandHandler("cancel", cancel_fsm)],
    allow_reentry=True
)

spoof_call_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(spoof_button_clicked, pattern="^startcall$")],
    states={
        VICTIM_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_victim_number_handler)],
        SPOOF_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_spoof_number_handler)],
        VICTIM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_victim_name_handler)],
        OTP_DIGIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_otp_digit_handler)]
    },
    fallbacks=[CommandHandler("cancel", cancel_fsm)],
    allow_reentry=True
)

if __name__ == "__main__":
    create_users_table()
    create_keys_table()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("keys", keys))
    application.add_handler(CommandHandler("cancel", cancel_fsm))
    application.add_handler(CallbackQueryHandler(reset_get_keys, pattern="^reset$|^get$"))
    application.add_handler(CallbackQueryHandler(choose_keys_type, pattern=r"^1DAYZ\+|3DAYZ\+|1WEEK\+|1MNTH\+|2HOUR\+"))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("update", update_numbers))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("phonelist", phonelist))
    application.add_handler(CommandHandler("plan", plan))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("setvoice", set_voice))
    application.add_handler(CallbackQueryHandler(chose_voice_accent, pattern="^setvoice$|^setaccent$"))
    application.add_handler(CallbackQueryHandler(choose_voice, pattern="^Jorch$|^William$|^Emma$|^Lara$"))
    application.add_handler(CallbackQueryHandler(choose_accent, pattern="^North America$|^Europe$|^Latin America$|^Asia & Pacific$|^Middle East & Africa$"))
    application.add_handler(CommandHandler(("call", "customcall"), caal_cuscaal))
    application.add_handler(CommandHandler("recall", recall))
    application.add_handler(CommandHandler("voicelist", voicelist))
    application.add_handler(CommandHandler(("paypal", "venmo", "applepay", "coinbase", "microsoft", "amazon", "quadpay", "cashapp", "citizens", "marcus", "carrier", "creditcard"), prenuilt_call))
    application.add_handler(CallbackQueryHandler(restart, pattern="^back1$|^back4$"))
    application.add_handler(CallbackQueryHandler(commands, pattern="^Commands$"))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(profile, pattern="^profile$"))
    application.add_handler(CallbackQueryHandler(features, pattern="^Features$"))
    application.add_handler(CallbackQueryHandler(community, pattern="^community$"))
    application.add_handler(CallbackQueryHandler(purchase_menu, pattern="^Purchase$"))
    application.add_handler(CommandHandler("purchase", purchase_menu))
    application.add_handler(CallbackQueryHandler(enter_menu, pattern="^Enter$"))
    application.add_handler(CallbackQueryHandler(prices_menu, pattern="^30$|^55$|^95$|^210$|^20$"))
    application.add_handler(CallbackQueryHandler(wallet_info, pattern=r"^btc\+|^usdt\+|^eth\+|^ltc\+|^sol\+"))
    application.add_handler(script_conv_handler)
    application.add_handler(CommandHandler("resetscript", resetscript))
    application.add_handler(CommandHandler("script", script_info))
    application.add_handler(spoof_call_conv_handler)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))
    application.run_polling()
