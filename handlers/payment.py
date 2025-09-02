from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
import logging

from models import User, CartItem, Order, OrderItem
from database import get_db
from states import CheckoutState
from keyboards import get_categories_keyboard
from config import API_TOKEN, ADMIN_CHAT_ID

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "✅ Завершить заказ")
async def start_checkout(message: types.Message, state: FSMContext):
    """Start the checkout process"""
    db = next(get_db())
    
    # Check if user is registered
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not user:
        await message.answer("❌ Сначала зарегистрируйтесь через /start")
        db.close()
        return
    
    # Get cart items
    cart_items = db.query(CartItem).filter(
        CartItem.user_telegram_id == message.from_user.id
    ).all()
    
    if not cart_items:
        await message.answer("❌ Ваша корзина пуста")
        db.close()
        return
    
    # Calculate totals
    total = sum(item.product.price * item.quantity for item in cart_items)
    prepayment = total * 0.2
    
    # Show order summary
    text = "📋 <b>Ваш заказ:</b>\n\n"
    
    for item in cart_items:
        product = item.product
        item_total = product.price * item.quantity
        text += f"▫️ {product.name}\n"
        text += f"   {item.quantity} x {product.price} = {item_total} СОМ\n\n"
    
    text += f"\n<b>💰 Итого к оплате: {total} СОМ</b>\n"
    text += f"<b>💸 Предоплата (20%): {prepayment} СОМ</b>\n\n"
    text += "📱 <b>Для оформления заказа:</b>\n"
    text += f"1. Переведите <b>{prepayment} СОМ</b> на указанный счет\n"
    text += "2. Отправьте фото чека об оплате\n\n"
    text += "💳 <b>Реквизиты для оплаты:</b>\n"
    text += "Мбанк: +996 555 123 456\n"
    text += "📸 <b>Отправьте фото чека об оплате:</b>"
    
    # Cancel button
    cancel_keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Отменить заказ")]],
        resize_keyboard=True
    )
    
    await message.answer(text, parse_mode="HTML", reply_markup=cancel_keyboard)
    await state.set_state(CheckoutState.waiting_for_payment)
    await state.update_data(total=total, prepayment=prepayment)
    
    db.close()

@router.message(CheckoutState.waiting_for_payment, F.photo)
async def process_payment_receipt(message: types.Message, state: FSMContext):
    """Process payment receipt photo"""
    data = await state.get_data()
    db = next(get_db())
    
    try:
        # Get user
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        # Get cart items again
        cart_items = db.query(CartItem).filter(
            CartItem.user_telegram_id == message.from_user.id
        ).all()
        
        if not cart_items:
            await message.answer("❌ Корзина пуста")
            db.close()
            await state.clear()
            return
        
        # Create order
        order = Order(
            user_id=user.id,
            total_amount=data['total'],
            prepayment=data['prepayment'],
            receipt_photo_id=message.photo[-1].file_id,
            status='pending'
        )
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items
        order_items_text = ""
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.add(order_item)
            order_items_text += f"▫️ {cart_item.product.name} x {cart_item.quantity} = {cart_item.product.price * cart_item.quantity} СОМ\n"
        
        # Clear cart
        db.query(CartItem).filter(
            CartItem.user_telegram_id == message.from_user.id
        ).delete()
        
        db.commit()
        
        # Send confirmation to user
        user_confirmation = (
            f"✅ <b>Ваш заказ #{order.id} принят!</b>\n\n"
            f"Ожидайте подтверждения от администратора.\n"
            f"Мы свяжемся с вами в ближайшее время.\n\n"
            f"📞 Ваш телефон: {user.phone}\n"
            f"📍 Адрес доставки: {user.address}"
        )
        
        await message.answer(user_confirmation, parse_mode="HTML", reply_markup=get_categories_keyboard())
        
        # Send order to admin
        admin_text = (
            f"🆕 <b>НОВЫЙ ЗАКАЗ #{order.id}</b>\n\n"
            f"👤 <b>Клиент:</b> {user.name}\n"
            f"💬 <b>Telegram:</b> @{message.from_user.username if message.from_user.username else 'нет username'}\n\n"
            f"📱 <b>Телефон:</b> {user.phone}\n"
            f"📍 <b>Адрес:</b> {user.address}\n"
            f"💰 <b>Сумма заказа:</b> {data['total']} СОМ\n"
            f"💸 <b>Предоплата (20%):</b> {data['prepayment']} СОМ\n\n"
            f"📦 <b>Товары:</b>\n{order_items_text}\n"
            f"🧾 <b>Чек об оплате приложен выше</b>\n\n"
            f"Для связи с клиентом:\n"
            f"👤 tg://user?id={user.telegram_id}"
        )

        # Send order to admin using the existing bot from message
        try:
            await message.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=admin_text,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send order to admin: {e}")
        
        logger.info(f"Order #{order.id} created and sent to admin")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при оформлении заказа. Попробуйте позже.")
        db.rollback()
    finally:
        db.close()

@router.message(CheckoutState.waiting_for_payment, F.text == "❌ Отменить заказ")
async def cancel_checkout(message: types.Message, state: FSMContext):
    """Cancel the checkout process"""
    await message.answer(
        "❌ Оформление заказа отменено.\n"
        "Ваша корзина сохранена.",
        reply_markup=get_categories_keyboard()
    )
    await state.clear()

@router.message(CheckoutState.waiting_for_payment)
async def invalid_payment_input(message: types.Message):
    """Handle invalid input during payment"""
    await message.answer(
        "📸 Пожалуйста, отправьте фото чека об оплате.\n"
        "Или нажмите '❌ Отменить заказ' для отмены."
    )