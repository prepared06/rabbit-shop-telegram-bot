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






@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """    
    if(db.subscriber_exists(message.from_user.id)):        
        await message.answer("Hi, " + message.from_user.first_name + ". We had a meeting already.")
    else:
        db.add_subscriber(message.from_user.id, message.from_user.full_name )    
        await message.reply("Hi! "+ message.from_user.first_name +"\nI'm EchoBot!\nPowered by aiogram.")
 
@dp.message_handler(commands=['products'])
async def send_products_list(message: types.Message):
    list_of_products = db.get_column('products_name', 'products_table')

    await message.answer("We have today this product list: " + list_of_products)

@dp.message_handler(commands=['add'])
async def add(message: types.Message):
    product = str(message.text).replace("/add ","")  
    if(db.product_exist(product)):
        id = db.get_product_id(product)
        db.add_order(message.from_user.id, id)
        await message.answer("I added " + product + " successful")
    else:
        await message.answer("There is no this product, try it one more time")
       

@dp.message_handler(commands = ['show'])
async def show_orders(message: types.Message):
    id = message.from_user.id
    res = db.get_product_list(id)
    await message.answer("You have this products in your bag:")
    for i in range(len(res)):
        await message.answer(res[i])

@dp.message_handler(commands = ['buy'])
async def buy(message: types.Message):
    id = message.from_user.id
    db.delete_orders_by_id_user(id)
    await message.answer("You just buyes all this stuff successful")


@dp.message_handler()
async def product_request(message: types.Message):

    exist_product = db.product_exist(message.text)
    
    if(exist_product):
        price = db.get_price(message.text)       
        await message.answer("There is some " + message.text)
        await message.answer("It costs " + price + " hottabych coins")
    else:
        await message.answer("There is no this product, try it one more time")







#@dp.message_handler()
#async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

  #  await message.answer(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)