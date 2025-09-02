from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from models import Category, Product, CartItem, Order, OrderItem, User
from database import get_db
from keyboards import get_product_keyboard, get_cart_keyboard, get_categories_keyboard
from states import ViewProduct

router = Router()
logger = logging.getLogger(__name__)

# ...existing code...

@router.message(lambda message: message.text and not message.text.startswith("/") and message.text not in ["⚙️ Настройки", "📁 Категории", "📊 Статистика", "📋 Заказы", "🔙 Главное меню", "🛒 Посмотреть корзину", "🗑 Очистить корзину", "✅ Завершить заказ", "🔙 Назад к покупкам"])
async def show_category_products(message: types.Message, state: FSMContext):
    """Handle category selection and show products"""
    
    logger.info(f"Category handler triggered for: {message.text}")
    
    db = next(get_db())
    
    try:
        # Check if this text matches any category
        category = None
        
        # Try exact match with emoji + name
        category = db.query(Category).filter(
            (Category.emoji + " " + Category.name) == message.text
        ).first()
        
        if not category:
            # Don't respond if it's not a category
            logger.info(f"No category found for: {message.text}")
            db.close()
            return
        
        logger.info(f"Found category: {category.name} (id: {category.id})")
        
        products = db.query(Product).filter(
            Product.category_id == category.id, 
            Product.active == True
        ).all()
        
        logger.info(f"Found {len(products)} products in category {category.name}")
        
        if not products:
            await message.answer("📭 В этой категории пока нет товаров.")
            db.close()
            return
        
        await state.update_data(
            category_id=category.id, 
            product_index=0, 
            products=[p.id for p in products]
        )
        
        await show_product(message, state, products[0], 0, len(products))
        await state.set_state(ViewProduct.viewing)
        
    except Exception as e:
        logger.error(f"Error in category handler: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при загрузке товаров.")
    finally:
        db.close()

# ...existing code...


async def show_product(message: types.Message, state: FSMContext, product: Product, index: int, total: int):
    """Display a single product with navigation"""
    keyboard = get_product_keyboard(product.id, message.from_user.id, index, total)
    
    caption = f"<b>{product.name}</b>\n\n"
    if product.description:
        caption += f"{product.description}\n\n"
    caption += f"💰 Цена: <b>{product.price} СОМ</b>\n"
    caption += f"📦 Товар {index + 1} из {total}"
    
    if product.photo_file_id:
        await message.answer_photo(
            photo=product.photo_file_id,
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    await state.set_state(ViewProduct.viewing)

@router.callback_query(ViewProduct.viewing, F.data.startswith("prev_"))
async def callback_prev_product(callback: types.CallbackQuery, state: FSMContext):
    """Navigate to previous product"""
    data = await state.get_data()
    products = data.get('products', [])
    # If category has only one product — notify and do nothing
    if len(products) <= 1:
        await callback.answer("❗ В этой категории только 1 товар", show_alert=False)
        return

    current_index = int(callback.data.split("_")[1])
    
    if current_index > 0:
        new_index = current_index - 1
    else:
        new_index = len(data['products']) - 1
    
    await state.update_data(product_index=new_index)
    
    db = next(get_db())
    product = db.query(Product).filter(Product.id == data['products'][new_index]).first()
    db.close()
    
    await show_product_edit(callback.message, state, product, new_index, len(data['products']))
    await callback.answer()

@router.callback_query(ViewProduct.viewing, F.data.startswith("next_"))
async def callback_next_product(callback: types.CallbackQuery, state: FSMContext):
    """Navigate to next product"""
    data = await state.get_data()
    products = data.get('products', [])
    # If category has only one product — notify and do nothing
    if len(products) <= 1:
        await callback.answer("❗ В этой категории только 1 товар", show_alert=False)
        return

    current_index = int(callback.data.split("_")[1])
    
    if current_index < len(data['products']) - 1:
        new_index = current_index + 1
    else:
        new_index = 0
    
    await state.update_data(product_index=new_index)
    
    db = next(get_db())
    product = db.query(Product).filter(Product.id == data['products'][new_index]).first()
    db.close()
    
    await show_product_edit(callback.message, state, product, new_index, len(data['products']))
    await callback.answer()

async def show_product_edit(message: types.Message, state: FSMContext, product: Product, index: int, total: int):
    """Edit existing message with new product"""
    keyboard = get_product_keyboard(product.id, message.chat.id, index, total)
    
    caption = f"<b>{product.name}</b>\n\n"
    if product.description:
        caption += f"{product.description}\n\n"
    caption += f"💰 Цена: <b>{product.price} СОМ</b>\n"
    caption += f"📦 Товар {index + 1} из {total}"
    
    if message.photo:
        if product.photo_file_id:
            await message.edit_media(
                media=types.InputMediaPhoto(media=product.photo_file_id, caption=caption, parse_mode="HTML"),
                reply_markup=keyboard
            )
        else:
            # Delete photo message and send text
            await message.delete()
            await message.answer(caption, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message.edit_text(caption, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(ViewProduct.viewing, F.data.startswith("next_"))
async def callback_next_product(callback: types.CallbackQuery, state: FSMContext):
    """Navigate to next product"""
    data = await state.get_data()
    products = data.get('products', [])
    # If category has only one product — notify and do nothing
    if len(products) <= 1:
        await callback.answer("❗ В этой категории только 1 товар", show_alert=False)
        return

    current_index = int(callback.data.split("_")[1])
    
    if current_index < len(products) - 1:
        new_index = current_index + 1
    else:
        new_index = 0
    
    await state.update_data(product_index=new_index)
    
    db = next(get_db())
    product = db.query(Product).filter(Product.id == products[new_index]).first()
    db.close()
    
    await show_product_edit(callback.message, state, product, new_index, len(products))
    await callback.answer()

@router.callback_query(ViewProduct.viewing, F.data.startswith("prev_"))
async def callback_prev_product(callback: types.CallbackQuery, state: FSMContext):
    """Navigate to previous product"""
    data = await state.get_data()
    products = data.get('products', [])
    # If category has only one product — notify and do nothing
    if len(products) <= 1:
        await callback.answer("❗ В этой категории только 1 товар", show_alert=False)
        return

    current_index = int(callback.data.split("_")[1])
    
    if current_index > 0:
        new_index = current_index - 1
    else:
        new_index = len(products) - 1
    
    await state.update_data(product_index=new_index)
    
    db = next(get_db())
    product = db.query(Product).filter(Product.id == products[new_index]).first()
    db.close()
    
    await show_product_edit(callback.message, state, product, new_index, len(products))
    await callback.answer()
    
@router.callback_query(ViewProduct.viewing, F.data.startswith("add_"))
async def callback_add_to_cart(callback: types.CallbackQuery, state: FSMContext):
    """Add product to cart"""
    product_id = int(callback.data.split("_")[1])
    db = next(get_db())
    
    cart_item = db.query(CartItem).filter(
        CartItem.user_telegram_id == callback.from_user.id,
        CartItem.product_id == product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(
            user_telegram_id=callback.from_user.id, 
            product_id=product_id, 
            quantity=1
        )
        db.add(cart_item)
    
    db.commit()
    
    product = db.query(Product).filter(Product.id == product_id).first()
    await callback.answer(f"✅ {product.name} добавлен в корзину")
    
    # Update keyboard to show new quantity
    data = await state.get_data()
    keyboard = get_product_keyboard(product_id, callback.from_user.id, data['product_index'], len(data['products']))
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    db.close()

@router.callback_query(ViewProduct.viewing, F.data.startswith("remove_"))
async def callback_remove_from_cart(callback: types.CallbackQuery, state: FSMContext):
    """Remove product from cart"""
    product_id = int(callback.data.split("_")[1])
    db = next(get_db())
    
    cart_item = db.query(CartItem).filter(
        CartItem.user_telegram_id == callback.from_user.id,
        CartItem.product_id == product_id
    ).first()
    
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.commit()
        else:
            db.delete(cart_item)
            db.commit()
        
        product = db.query(Product).filter(Product.id == product_id).first()
        await callback.answer(f"➖ {product.name} удален из корзины")
    else:
        await callback.answer("❌ Товар не найден в корзине")
    
    # Update keyboard to show new quantity
    data = await state.get_data()
    keyboard = get_product_keyboard(product_id, callback.from_user.id, data['product_index'], len(data['products']))
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    db.close()

@router.callback_query(F.data == "back_categories")
async def callback_back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    """Go back to category selection"""
    await callback.message.delete()
    await callback.message.answer("Выберите категорию:", reply_markup=get_categories_keyboard())
    await state.clear()
    await callback.answer()

@router.message(F.text == "🛒 Посмотреть корзину")
async def show_cart(message: types.Message):
    """Display user's cart"""
    db = next(get_db())
    
    cart_items = db.query(CartItem).filter(
        CartItem.user_telegram_id == message.from_user.id
    ).all()
    
    if not cart_items:
        await message.answer("🛒 Ваша корзина пуста")
        db.close()
        return
    
    text = "🛒 <b>Ваша корзина:</b>\n\n"
    total = 0
    
    for item in cart_items:
        product = item.product
        item_total = product.price * item.quantity
        total += item_total
        
        text += f"▫️ {product.name}\n"
        text += f"   {item.quantity} x {product.price} = {item_total} СОМ\n\n"
    
    text += f"<b>Итого: {total} СОМ</b>\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_cart_keyboard())
    db.close()

@router.message(F.text == "🗑 Очистить корзину")
async def clear_cart(message: types.Message):
    """Clear all items from cart"""
    db = next(get_db())
    
    db.query(CartItem).filter(
        CartItem.user_telegram_id == message.from_user.id
    ).delete()
    db.commit()
    db.close()
    
    await message.answer("🗑 Корзина очищена", reply_markup=get_categories_keyboard())

@router.message(F.text == "🔙 Назад к покупкам")
async def back_to_shopping(message: types.Message):
    """Return to category selection"""
    await message.answer("Выберите категорию:", reply_markup=get_categories_keyboard())