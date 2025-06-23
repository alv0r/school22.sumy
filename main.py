import os
from datetime import datetime
from flask import Flask, redirect, url_for, render_template, flash, request, abort, jsonify
from sqlalchemy.orm import joinedload

from db import db, init_db, MenuItem, News
from flask_login import LoginManager, current_user, login_required
from flask import request
from flask_login import LoginManager
from db import User
from werkzeug.utils import secure_filename
from unidecode import unidecode

def generate_slug(title):
    return unidecode(title.lower().replace(' ', '_'))

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Створення папки якщо не існує
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'upload' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['upload']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        file_url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({"url": file_url})

    return jsonify({"error": "Invalid file type"}), 400

from routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    db_name = "SITE.db"
    app.secret_key = "some_very_secret_string"

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth_bp.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    if not os.path.exists(db_name):
        print("База даних не знайдена. Створюємо нову...")
        init_db(app)
    else:
        with app.app_context():
            db.create_all()
        init_db(app)

    def build_menu_structure():
        menu_items = []
        main_items = MenuItem.query.filter_by(parent_id=None).all()

        for main_item in main_items:
            submenu = MenuItem.query.filter_by(parent_id=main_item.id).all()
            menu_items.append({
                'title': main_item.title,
                'url': main_item.url,
                'slug': main_item.slug,
                'submenu': [{'title': sub.title, 'url': sub.url} for sub in submenu] if submenu else None
            })

        return menu_items

    # Автоматичне додавання меню та новин у всі шаблони
    @app.context_processor
    def inject_globals():
        return {
            'menu_items': build_menu_structure(),
            'latest_news': News.query.order_by(News.created_at.desc()).limit(5).all()
        }

    # Тепер можна писати маршрути без menu_items та latest_news вручну

    @app.route('/')
    def index():
        return render_template('index.html', menu_items=build_menu_structure(),
                               latest_news=News.query.order_by(News.created_at.desc()).limit(5).all())


    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash("Доступ заборонено.")
            return redirect(url_for('index'))
        return render_template('admin_dashboard.html')




    @app.route('/admin/menu')
    @login_required
    def menu_list():
        if not current_user.is_admin:
            flash("Доступ заборонено.")
            return redirect(url_for('index'))
        menu_items = MenuItem.query.filter_by(parent_id=None).all()
        return render_template('admin_menu_list.html', menu_items=menu_items)

    @app.route('/admin/menu/delete/<int:item_id>')
    @login_required
    def delete_menu(item_id):
        if not current_user.is_admin:
            flash("Доступ заборонено.")
            return redirect(url_for('index'))
        item = MenuItem.query.get_or_404(item_id)
        if not item.parent_id:
            for child in item.submenu:
                db.session.delete(child)
        db.session.delete(item)
        db.session.commit()
        flash("Пункт меню успішно видалено.")
        return redirect(url_for('menu_list'))

    @app.route('/admin/menu/create', methods=['GET', 'POST'])
    @login_required
    def create_menu():
        if not current_user.is_admin:
            flash("Доступ заборонено.")
            return redirect(url_for('index'))

        if request.method == 'POST':
            title = request.form['title']
            slug = request.form['slug']
            url = request.form.get('url')
            content = request.form.get('content')
            parent_id = request.form.get('parent_id') or None

            new_item = MenuItem(
                title=title,
                slug=slug,
                url=url,
                content=content,
                parent_id=parent_id
            )
            db.session.add(new_item)
            db.session.commit()
            flash("Пункт меню створено.")
            return redirect(url_for('admin_dashboard'))

        parents = MenuItem.query.filter_by(parent_id=None).all()
        return render_template('admin_create_menu.html', parents=parents)

    @app.route('/admin/edit/<int:item_id>', methods=['GET', 'POST'])
    @login_required
    def edit_menu_content(item_id):
        item = MenuItem.query.get_or_404(item_id)
        if request.method == 'POST':
            item.title = request.form['title']
            item.slug = generate_slug(item.title)
            item.url = f"/page/{item.slug}"
            item.content = request.form['content']
            db.session.commit()
            flash('Пункт оновлено.')
            return redirect(url_for('menu_list'))
        return render_template('admin_edit_menu.html', item=item)

    @app.route('/page/<slug>')
    def view_menu_page(slug):
        item = MenuItem.query.filter_by(slug=slug).first_or_404()
        menu_items = MenuItem.query.all()

        active_parent_slug = None
        for parent in menu_items:
            if parent.submenu:
                for sub in parent.submenu:
                    if sub.slug == slug:
                        active_parent_slug = parent.slug
                        break

        return render_template('menu_page.html',
                               item=item,
                               active_slug=slug,
                               active_parent_slug=active_parent_slug)



    @app.route('/news')
    def all_news():
        news_list = News.query.order_by(News.created_at.desc()).all()
        return render_template('news_list.html', news_list=news_list)

    @app.route('/news/<int:news_id>')
    def view_news(news_id):
        article = News.query.get_or_404(news_id)
        return render_template('view_news.html', article=article)

    @app.route('/admin/news')
    @login_required
    def admin_news_list():
        if not current_user.is_admin:
            abort(403)
        articles = News.query.order_by(News.created_at.desc()).all()
        return render_template('admin_news_list.html', articles=articles)



    @app.route('/admin/news/create', methods=['GET', 'POST'])
    @login_required
    def admin_create_news():
        if not current_user.is_admin:
            abort(403)
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            image = request.form['image']
            news = News(title=title, content=content, image=image)
            db.session.add(news)
            db.session.commit()
            return redirect(url_for('admin_news_list'))
        return render_template('admin_create_news.html')

    @app.route('/admin/news/edit/<int:news_id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit_news(news_id):
        if not current_user.is_admin:
            abort(403)
        article = News.query.get_or_404(news_id)
        if request.method == 'POST':
            article.title = request.form['title']
            article.content = request.form['content']
            article.image = request.form['image']
            db.session.commit()
            return redirect(url_for('admin_news_list'))
        return render_template('admin_edit_news.html', article=article)

    @app.route('/admin/news/delete/<int:news_id>', methods=['POST'])
    @login_required
    def admin_delete_news(news_id):
        if not current_user.is_admin:
            abort(403)
        article = News.query.get_or_404(news_id)
        db.session.delete(article)
        db.session.commit()
        return redirect(url_for('admin_news_list'))

    app.register_blueprint(auth_bp)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)