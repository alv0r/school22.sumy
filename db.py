from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)  # Назва файлу зображення в /static/uploads
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<News {self.title}>'


class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=True)  # може бути пусте, якщо є сабменю
    slug = db.Column(db.String(255), unique=True,
                     nullable=False)  # коротка назва для ідентифікації (типу school, student)
    parent_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    content = db.Column(db.Text, nullable=True)

    parent = db.relationship('MenuItem', remote_side=[id], backref='submenu')

    def __repr__(self):
        return f'<MenuItem {self.title}>'





def init_db(app):
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

        if not News.query.first():
            sample_news = [
                News(
                    title='26 квітня — 39-та річниця Чорнобильської трагедії',
                    image='chernobyl.jpg',
                    content='Пам’ятаємо. Шануємо. Вічна слава героям Чорнобиля.'
                ),
                News(
                    title='До уваги батьків майбутніх першокласників!',
                    image='schoolkids.jpg',
                    content='Оголошено набір у перші класи на 2025-2026 навчальний рік.'
                ),
                News(
                    title='Лекторій «Тайм-менеджмент у професійній діяльності педагога»',
                    image='lecture.jpg',
                    content='Педагоги школи пройшли тренінг із сучасного планування робочого часу.'
                )
            ]
            db.session.add_all(sample_news)
            db.session.commit()

        if not MenuItem.query.first():
            # Ініціалізація головних пунктів меню
            school = MenuItem(title='ПРО ШКОЛУ', url='#', slug='pro-shkolu')
            enrollment = MenuItem(title='Зарахування до закладу освіти', url='#', slug='zarahuvannya')
            news = MenuItem(title='Новини', url='#', slug='novyny')
            contacts = MenuItem(title='Контакти', url='#', slug='kontakty')
            education_law = MenuItem(title='Виконання вимог ст.30 Закону України "Про освіту"', url='#',
                                     slug='pro-osvitu')
            state_control = MenuItem(title='Результати державного контролю', url='#', slug='derzhkontrol')
            education_process = MenuItem(title='Освітній процес', url='#', slug='osvitnij-proces')
            together_loss = MenuItem(title='Долаємо освітні втрати разом', url='#', slug='dolajemo-vtraty')
            hmt2025 = MenuItem(title='НМТ - 2025', url='#', slug='nmt-2025')
            healthy_eating = MenuItem(title='Здорове харчування', url='#', slug='zdorove-harchuvannya')
            distance_learning = MenuItem(title='Дистанційне навчання', url='#', slug='distancijne-navchannya')
            bullying = MenuItem(title='Актуальне: Булінг', url='#', slug='buling')
            upbringing = MenuItem(title='Виховна робота', url='#', slug='vykhovna-robota')
            self_government = MenuItem(title='Учнівське самоврядування', url='#', slug='samospravy')
            vacations = MenuItem(title='Канікули', url='#', slug='kanikuly')
            psychological_service = MenuItem(title='Психологічна служба', url='#', slug='psyhologichna-sluzhba')
            gender_equality = MenuItem(title='Гендерна рівність', url='#', slug='gender-equality')
            safe_environment = MenuItem(title='Безпечне освітнє середовище', url='#', slug='safe-environment')
            library = MenuItem(title='Шкільна бібліотека', url='#', slug='library')
            finance = MenuItem(title='Фінансова діяльність', url='#', slug='finansy')
            energy_saving = MenuItem(title='Енергозбереження', url='#', slug='energozberezhennya')
            questions = MenuItem(title='Запитуйте - відповімо', url='#', slug='faq')
            calendar = MenuItem(title='Календар', url='#', slug='calendar')

            db.session.add_all([
                school, enrollment, news, contacts, education_law, state_control,
                education_process, together_loss, hmt2025, healthy_eating, distance_learning,
                bullying, upbringing, self_government, vacations, psychological_service,
                gender_equality, safe_environment, library, finance, energy_saving, questions, calendar
            ])
            db.session.commit()

            # Додаємо підпункти
            submenus = [
                # ПРО ШКОЛУ
                ('Територія обслуговування школи', school.id),
                ('Візитка школи, Мережа класів', school.id),
                ('Структура та органи управління закладу освіти', school.id),
                ('Кадровий склад', school.id),
                ('Атестація педагогічних працівників', school.id),
                ('Правила поведінки учасників освітнього процесу', school.id),
                ('Матеріально-технічне забезпечення', school.id),
                ('Вимоги до навчального кабінету', school.id),
                ('Шкільна кінопанорама', school.id),
                ('Історія школи', school.id),
                ('Галерея', school.id),
                ('Незабутні шкільні роки (2017-2018)', school.id),

                # Зарахування
                ('Зарахування до 1 класу', enrollment.id),

                # Виконання вимог закону
                ('Положення про внутрішню систему забезпечення якості освіти', education_law.id),
                ('Положення про академічну доброчесність', education_law.id),
                ('Індивідуальна форма навчання', education_law.id),
                ('Організація інклюзивного навчання', education_law.id),
                ('Вакансії', education_law.id),
                ('Робота зі зверненнями громадян', education_law.id),
                ('Звіт про діяльність закладу освіти', education_law.id),
                ('Звіт керівника', education_law.id),

                # Освітній процес
                ('Режим роботи', education_process.id),
                ('Розклад уроків', education_process.id),
                ('Освітні програми', education_process.id),
                ('Освітні компоненти', education_process.id),
                ('Критерії оцінювання навчальних досягнень учнів', education_process.id),
                ('Нова українська школа', education_process.id),
                ('На допомогу вчителю НУШ', education_process.id),
                ('Методична робота школи І ступеня', education_process.id),
                ('Новий освітній простір', education_process.id),
                ('Методична робота', education_process.id),
                ('Професійна рада', education_process.id),
                ('Предметні тижні', education_process.id),
                ('Сайти, блоги вчителів', education_process.id),
                ('Робота з талановитою молоддю', education_process.id),
                ('Результати моніторингу якості освіти', education_process.id),

                # Здорове харчування
                ('Батькам про здорове харчування', healthy_eating.id),
                ('Учням про здорове харчування', healthy_eating.id),

                # Булінг
                ('Нормативно-правова база з питань булінгу', bullying.id),
                ('Права та обов\'язки учня', bullying.id),
                ('Правила поведінки здобувачів освіти', bullying.id),
                ('План заходів проти булінгу', bullying.id),
                ('Порядок подання та розгляду заяв', bullying.id),
                ('Порядок реагування на випадки булінгу', bullying.id),
                ('Відповідальні особи', bullying.id),
                ('Телефони довіри', bullying.id),
                ('Корисні поради', bullying.id),
                ('Поради учням', bullying.id),
                ('Поради батькам', bullying.id),
                ('Поради вчителям', bullying.id),
                ('Інформаційні матеріали', bullying.id),
                ('Всеукраїнська акція "16 днів проти насильства"', bullying.id),

                # Виховна робота
                ('Нормативно-правове забезпечення виховної роботи', upbringing.id),
                ('Система виховної роботи', upbringing.id),
                ('Класному керівнику', upbringing.id),
                ('Патріотичне виховання', upbringing.id),
                ('Рій "Краяни"', upbringing.id),
                ('КНИГА ЗВІТІВ рою "Краяни"', upbringing.id),
                ('Профілактика правопорушень та злочинності', upbringing.id),
                ('Робота з батьками', upbringing.id),
                ('Профорієнтаційна робота', upbringing.id),

                # Психологічна служба
                ('Національна дитяча гаряча лінія', psychological_service.id),
                ('Всеукраїнська програма ментального здоров\'я "Ти як?"', psychological_service.id),

                # Безпечне освітнє середовище
                ('Безпека життєдіяльності', safe_environment.id),
                ('Безпека дорожнього руху', safe_environment.id),
                ('Безпека в Інтернеті', safe_environment.id),
                ('Про протидію онлайн шахрайствам', safe_environment.id),
                ('Цивільний захист', safe_environment.id),
                ('Платформа МРІЯ', safe_environment.id),
                ('БРАМА - онлайн варта України', safe_environment.id),

                # Бібліотека
                ('Електронні підручники', library.id),
                ('Місячник шкільної бібліотеки', library.id),
                ('Конкурсний відбір проєктів учнів', library.id),
                ('Виховна робота бібліотеки', library.id),
                ('Новинки літератури', library.id),
                ('Літературні виставки', library.id),
                ('Медіатека', library.id),
                ('Букстейлери', library.id),
                ('Що читати учням влітку', library.id),

                # Фінансова діяльність
                ('Кошторис', finance.id),
                ('Капітальні ремонти', finance.id),
                ('Предмети закупівлі', finance.id)
            ]

            db.session.add_all([MenuItem(title=title, url='#',
                                         slug=title.lower().replace(' ', '-').replace('"', '').replace('\'', ''),
                                         parent_id=parent_id) for title, parent_id in submenus])
            db.session.commit()




