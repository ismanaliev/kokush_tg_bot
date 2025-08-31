from database import engine, Base
from models import Category
from sqlalchemy.orm import sessionmaker

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Add initial categories
categories = [
    {'name': 'Ручки', 'emoji': '✍️'},
    {'name': 'Тетради', 'emoji': '📒'},
    {'name': 'Книги', 'emoji': '📚'},
    {'name': 'Предметы для ИЗО', 'emoji': '🎨'},
    {'name': 'Карандаши', 'emoji': '✏️'},
    {'name': 'Обложки', 'emoji': '📗'},
    {'name': 'Маркеры и фломастеры', 'emoji': '🖍'},
    {'name': 'Прописи', 'emoji': '📝'}
]

for cat_data in categories:
    if not session.query(Category).filter(Category.name == cat_data['name']).first():
        category = Category(**cat_data)
        session.add(category)

session.commit()
session.close()

print("Database initialized with categories!")