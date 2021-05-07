#aiobot libs
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

#config
from config import API_TOKEN, id_manager


# Configure logging
logging.basicConfig(level=logging.INFO)

#database
from dbManage import DBManage
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

db = DBManage()

#buttons
inline_btn_products = InlineKeyboardButton('Products', callback_data='products')
inline_btn_shopping_cart = InlineKeyboardButton('Shopping cart', callback_data='shopping_cart')
inline_btn_clear_all_shopping_cart = InlineKeyboardButton('Clear shopping cart', callback_data='clear')
inline_btn_make_order = InlineKeyboardButton('Make order', callback_data = 'make_order')
inline_btn_back_to_main_menu = InlineKeyboardButton('Back', callback_data = 'back')

#menus
inline_menu_keyboard = InlineKeyboardMarkup().add(inline_btn_products).add(inline_btn_shopping_cart)
product_menu_keyboard = InlineKeyboardMarkup()
shopping_cart_menu = InlineKeyboardMarkup().add(inline_btn_make_order).add(inline_btn_clear_all_shopping_cart).add(inline_btn_back_to_main_menu)


#
@dp.message_handler(commands=['help'])
async def help_info(message: types.Message):
    await message.answer("Bot-online shop will help you to make order.")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):     
    if(db.subscriber_exists(message.from_user.id)):        
        await message.answer("Hi, " + message.from_user.first_name + \
           ". We had a meeting already.",\
           reply_markup = inline_menu_keyboard)
    else:
        db.add_subscriber(message.from_user.id, message.from_user.full_name )    
        await message.reply("Hi! "+ message.from_user.first_name +"\nI'm shop bot, you can buy some products using me. Just choose what you want in menu!", \
           reply_markup = inline_menu_keyboard)
 
#handler for button "products" from main menu
@dp.callback_query_handler(lambda k: k.data == "products")
async def send_products_list(callback_query: CallbackQuery):  
    
    list_of_products = db.get_list_of_elements_from_products()#list with tuplets (id, products name, price)

    product_menu_keyboard = InlineKeyboardMarkup()

    for a in range(len(list_of_products)):
        products_id = str(list_of_products[a][0])
        products_name = list_of_products[a][1]#products name
        products_price = str(list_of_products[a][2])#price
        inline_btn_var = InlineKeyboardButton(products_name + ": " + products_price + " hottabych coins", callback_data='_products_id_' + products_id)
        product_menu_keyboard.add(inline_btn_var)

    product_menu_keyboard.add(inline_btn_shopping_cart)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "We have today this product list: ", reply_markup = product_menu_keyboard)

 #handler for buttons from menus   
@dp.callback_query_handler(lambda k: k.data.startswith("_products_id_"))
async def products_id_handler(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    product_id = callback_query.data.replace("_products_id_","")   
    db.add_order(callback_query.from_user.id, product_id)
    await bot.send_message(callback_query.from_user.id, "Product was succesfull added to your shopping cart!", reply_markup = product_menu_keyboard)

#handler for shoping cart  button
@dp.callback_query_handler(lambda k: k.data == "shopping_cart")
async def shoping_cart(callback_query: CallbackQuery):
    id = callback_query.from_user.id
    res = db.get_product_list(id)
    price = 0
    answer_str = "In your shoping cart is/are next position: "
    if(res):
        for i in range(len(res)):
            answer_str = answer_str + res[i] +", "
            price += int(db.get_price(res[i]))
    else:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Your shoping cart is empty now.", reply_markup = inline_menu_keyboard)     
        return
    answer_str += " total cost is " + str(price) + " hottabych coins"
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, answer_str, reply_markup = shopping_cart_menu )

#handler for maker order(delete order drom db + send message to manager)
@dp.callback_query_handler(lambda k: k.data == "make_order")
async def make_order(callback_query: CallbackQuery):
    id = callback_query.from_user.id
    res = db.get_product_list(id)
    price = 0
    list_product_str = ""
    await bot.answer_callback_query(callback_query.id)
    if(res):
        db.delete_orders_by_id_user(id)      
        for i in range(len(res)):
            list_product_str = list_product_str + res[i] +", "
            price += int(db.get_price(res[i]))
        text_for_manager = "User " + callback_query.from_user.full_name + " with id " + str(callback_query.from_user.id) + " just \
made order. Customers order: " +  list_product_str + ". Total price: " + str(price)  + " hottabych coins"
        await bot.send_message(id_manager, text_for_manager)
        await bot.send_message(id, "We sended message to our manager. He will contact with you soon. Thank you for using our service!", reply_markup = inline_menu_keyboard)
    else:
        await bot.send_message(id, "Your shoping cart is empty now! Try to add something to your order.", reply_markup = product_menu_keyboard)
        
#handler clear shoping cart
@dp.callback_query_handler(lambda k: k.data == "clear")
async def clear_shoping_cart(callback_query: CallbackQuery):
    id = callback_query.from_user.id
    res = db.get_product_list(id)
    await bot.answer_callback_query(callback_query.id)
    if(res):
        db.delete_orders_by_id_user(id)
        await bot.send_message(id, "Your shopping cart is empty now!", reply_markup = inline_menu_keyboard)
    else:
        await bot.send_message(id, "Your shopping cart is already empty!", reply_markup = inline_menu_keyboard)

#handler for back
@dp.callback_query_handler(lambda k: k.data == "back")
async def back_to_main_menu(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Welcome to main menu", reply_markup = inline_menu_keyboard )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)