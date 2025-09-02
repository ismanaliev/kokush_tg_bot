from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import func
from models import Category, Product, Order, User
from database import get_db
from config import ADMIN_CHAT_ID
from states import AdminProductAdd
from keyboards import get_admin_keyboard, get_categories_keyboard

router = Router()

def is_admin(message: types.Message) -> bool:
    return message.from_user.id == ADMIN_CHAT_ID

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message):
        return
    
    admin_text = (
        "👨‍💼 <b>Панель администратора</b>\n\n"
        "Выберите действие с помощью кнопок ниже:"
    )
    
    await message.answer(admin_text, parse_mode="HTML", reply_markup=get_admin_keyboard())

@router.message(F.text == "⚙️ Настройки")
async def manage_products(message: types.Message):
    if not is_admin(message):
        return
    
    text = (
        "📦 <b>Управление товарами</b>\n\n"
        "<b>Команды:</b>\n"
        "/add_product - Добавить новый товар\n"
        "/list_products - Показать все товары\n"
        "/delete_product ID - Удалить товар\n"
        "/delete_category ID - Удалить категорию\n"
        "/add_category NAME - Добавить новую категорию\n"
    )
    
    await message.answer(text, parse_mode="HTML")

@router.message(Command("add_product"))
async def start_add_product(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    
    db = next(get_db())
    categories = db.query(Category).all()
    
    if not categories:
        await message.answer("❌ Сначала создайте категории!")
        db.close()
        return
    
    text = "Выберите категорию для товара:\n\n"
    for cat in categories:
        text += f"{cat.id}. {cat.emoji} {cat.name}\n"
    
    text += "\nВведите ID категории:"
    
    await message.answer(text)
    await state.set_state(AdminProductAdd.waiting_for_category)
    db.close()


@router.message(AdminProductAdd.waiting_for_category)
async def add_product_category(message: types.Message, state: FSMContext):
    try:
        category_id = int(message.text)
        db = next(get_db())
        
        if not db.query(Category).filter(Category.id == category_id).first():
            await message.answer("❌ Категория не найдена. Введите корректный ID.")
            db.close()
            return
        
        db.close()
        await state.update_data(category_id=category_id)
        await message.answer("📝 Введите название товара:")
        await state.set_state(AdminProductAdd.waiting_for_name)
    except:
        await message.answer("❌ Введите корректный ID категории (число)")

@router.message(AdminProductAdd.waiting_for_name)
async def add_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📄 Введите описание товара (или отправьте - для пропуска):")
    await state.set_state(AdminProductAdd.waiting_for_description)

@router.message(AdminProductAdd.waiting_for_description)
async def add_product_description(message: types.Message, state: FSMContext):
    description = None if message.text == "-" else message.text
    await state.update_data(description=description)
    await message.answer("💰 Введите цену товара (в СОМ):")
    await state.set_state(AdminProductAdd.waiting_for_price)

@router.message(AdminProductAdd.waiting_for_price)
async def add_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("📸 Отправьте фото товара (или отправьте - для пропуска):")
        await state.set_state(AdminProductAdd.waiting_for_photo)
    except:
        await message.answer("❌ Введите корректную цену (число)")

@router.message(AdminProductAdd.waiting_for_photo, F.photo)
async def add_product_with_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db = next(get_db())
    
    product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        photo_file_id=message.photo[-1].file_id,
        category_id=data['category_id']
    )
    
    db.add(product)
    db.commit()
    db.close()
    
    await message.answer(f"✅ Товар '{data['name']}' успешно добавлен с фото!")
    await state.clear()

@router.message(AdminProductAdd.waiting_for_photo)
async def add_product_without_photo(message: types.Message, state: FSMContext):
    if message.text == "-":
        data = await state.get_data()
        db = next(get_db())
        
        product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category_id=data['category_id']
        )
        
        db.add(product)
        db.commit()
        db.close()
        
        await message.answer(f"✅ Товар '{data['name']}' успешно добавлен!")
        await state.clear()
    else:
        await message.answer("📸 Пожалуйста, отправьте фото или - для пропуска")

@router.message(Command("list_products"))
async def list_products(message: types.Message):
    if not is_admin(message):
        return
    
    db = next(get_db())
    products = db.query(Product).filter(Product.active == True).all()
    
    if not products:
        await message.answer("📦 Товары отсутствуют.")
        db.close()
        return
    
    text = "📦 <b>Список товаров:</b>\n\n"
    for prod in products:
        text += f"{prod.id}. {prod.name} - {prod.price} СОМ\n"
        text += f"   📁 {prod.category.emoji} {prod.category.name}\n\n"
    
    await message.answer(text, parse_mode="HTML")
    db.close()

@router.message(F.text == "🔙 Главное меню")
async def back_to_main(message: types.Message):
    if not is_admin(message):
        return
    
    await message.answer("Выберите категорию:", reply_markup=get_categories_keyboard())

@router.message(Command("add_category"))
async def add_category(message: types.Message):
    if not is_admin(message):
        return

    # Ожидается: /add_category 😊 Название
    rest = message.text.partition(" ")[2].strip()
    if not rest:
        await message.answer("Использование: /add_category <emoji> <name>\nПример: /add_category 🧸 Игрушки")
        return

    try:
        emoji, name = rest.split(maxsplit=1)
    except ValueError:
        await message.answer("Ошибка формата. Использование: /add_category <emoji> <name>")
        return

    db = next(get_db())
    # Проверка на существующую категорию с таким именем (регистронезависимо)
    if db.query(Category).filter(func.lower(Category.name) == name.lower()).first():
        await message.answer("❌ Категория с таким именем уже существует.")
        db.close()
        return

    new_cat = Category(name=name, emoji=emoji)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    db.close()

    await message.answer(f"✅ Категория добавлена: {new_cat.id}. {new_cat.emoji} {new_cat.name}")

@router.message(Command("delete_category"))
async def delete_category(message: types.Message):
    if not is_admin(message):
        return

    # Ожидается: /delete_category 3
    rest = message.text.partition(" ")[2].strip()
    if not rest:
        await message.answer("Использование: /delete_category <id>\nПример: /delete_category 3")
        return

    try:
        cat_id = int(rest.split()[0])
    except ValueError:
        await message.answer("❌ Введите корректный ID (число).")
        return

    db = next(get_db())
    category = db.query(Category).filter(Category.id == cat_id).first()
    if not category:
        await message.answer("❌ Категория не найдена.")
        db.close()
        return

    product_count = db.query(Product).filter(Product.category_id == cat_id).count()

    if product_count == 1:
        # Если в категории только один товар — уведомляем и не удаляем
        await message.answer(f"❗ Категория '{category.name}' содержит только 1 товар. Удаление не требуется.")
        db.close()
        return

    if product_count > 1:
        # Если больше одного товара — отказываем в удалении
        await message.answer(
            f"❌ Нельзя удалить категорию: в ней {product_count} товаров. Удалите товары или переместите их в другую категорию."
        )
        db.close()
        return

    # product_count == 0 → безопасно удалить
    db.delete(category)
    db.commit()
    db.close()

    await message.answer(f"✅ Категория {cat_id} удалена.")

#Categories

@router.message(F.text == "📁 Категории")
async def manage_categories(message: types.Message):
    if not is_admin(message):
        return
    
    db = next(get_db())
    categories = db.query(Category).all()
    
    text = "📁 <b>Категории:</b>\n\n"
    for cat in categories:
        product_count = db.query(Product).filter(Product.category_id == cat.id).count()
        text += f"{cat.id}. {cat.emoji} {cat.name} ({product_count} товаров)\n"
    
    db.close()
    await message.answer(text, parse_mode="HTML")

#Statistics

@router.message(F.text == "📊 Статистика")
async def show_statistics(message: types.Message):
    if not is_admin(message):
        return
    
    db = next(get_db())
    
    total_users = db.query(User).count()
    total_products = db.query(Product).filter(Product.active == True).count()
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    
    # Calculate total revenue
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    
    text = (
        "📊 <b>Статистика магазина:</b>\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"📦 Активных товаров: {total_products}\n"
        f"📋 Всего заказов: {total_orders}\n"
        f"⏳ Ожидают обработки: {pending_orders}\n"
        f"💰 Общая выручка: {total_revenue} СОМ"
    )
    
    db.close()
    await message.answer(text, parse_mode="HTML")

#Orders

@router.message(F.text == "📋 Заказы")
async def show_orders(message: types.Message):
    if not is_admin(message):
        return
    
    db = next(get_db())
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
    
    if not orders:
        await message.answer("📋 Заказов пока нет.")
        db.close()
        return
    
    text = "📋 <b>Последние заказы:</b>\n\n"
    for order in orders:
        text += (
            f"Заказ #{order.id} от {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"Клиент: {order.user.name}\n"
            f"Сумма: {order.total_amount} СОМ\n"
            f"Статус: {order.status}\n\n"
        )
    
    db.close()
    await message.answer(text, parse_mode="HTML")