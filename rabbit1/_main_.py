#aiobot libs
import logging
from aiogram import Bot, Dispatcher, executor, types


#config
from config import API_TOKEN


# Configure logging
logging.basicConfig(level=logging.INFO)

#database
from dbManage import DBManage
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

db = DBManage()

commands = """
    /products - type it if you wanna get available products
    /add - to add to your bag some product type /add product name
           for exemple: \"/add potatto\"
    /show - to see your order type it
    /buy - to make payment type it

     also if you wanna check price you must just write name of product
"""

@dp.message_handler(commands=['help'])
async def help_info(message: types.Message):
    await message.answer("We have this commands:\n" + commands)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """    
    if(db.subscriber_exists(message.from_user.id)):        
        await message.answer("Hi, " + message.from_user.first_name + ". We had a meeting already.\nTry to /help")
    else:
        db.add_subscriber(message.from_user.id, message.from_user.full_name )    
        await message.reply("Hi! "+ message.from_user.first_name +"\nI'm EchoBot!\nPowered by aiogram.")
 
@dp.message_handler(commands=['products'])
async def send_products_list(message: types.Message):
    list_of_products = db.get_column('products_name', 'products_table')

    await message.answer("We have today this product list: " + list_of_products + "\nPlease, write product to get price for it")

@dp.message_handler(commands=['add'])
async def add(message: types.Message):
    product = str(message.text).replace("/add ","")  
    

    if(db.product_exist(product)):
        id = db.get_product_id(product)
        db.add_order(message.from_user.id, id)
        await message.answer("I added " + product + " successful\nTry /show to check your bag")
    elif ("/add" in product):
        await message.answer("Please, type /add product name\nfor exemple: \"/add potatto\"")
    else:
        await message.answer("There is no this product, try it one more time")
       

@dp.message_handler(commands = ['show'])
async def show_orders(message: types.Message):
    price = 0
    id = message.from_user.id
    res = db.get_product_list(id)
    if(res):
        await message.answer("You have this products in your bag:")
        for i in range(len(res)):
            await message.answer(res[i])
            price += int(db.get_price(res[i]))
        await message.answer("Total price is " + str(price) + " hottabych coins\nYou can buy it now using /buy")
    else:
        await message.answer("Your bag is empty now. Type /products to get products list.")


#this is simply realisation scenario of buying
#my goal here was not make money transaction, I wanna clear orders in DB 
#in future I am planning to add transaction
@dp.message_handler(commands = ['buy'])
async def buy(message: types.Message):
    id = message.from_user.id
    res = db.get_product_list(id)
    if(res):
        db.delete_orders_by_id_user(id)
        await message.answer("You just buyes all this stuff successful")
    else:
        await message.answer("Your bag is empty now! Try to /add something to your order.")

#handler get any message which is not registered like commands
#I use it for processing products names
@dp.message_handler()
async def product_request(message: types.Message):

    exist_product = db.product_exist(message.text)
    
    if(exist_product):
        price = db.get_price(message.text)       
        await message.answer("There is some " + message.text)
        await message.answer("It costs " + price + " hottabych coins\nYou can add it to your bag. Just type /add " + message.text)
    else:
        await message.answer("There is no this product, try it one more time")







#@dp.message_handler()
#async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

  #  await message.answer(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)