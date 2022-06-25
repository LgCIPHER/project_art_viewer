from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import os.path

from Reddit_API import check_deleted_img

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pic.db'
db = SQLAlchemy(app)

# should put this information else where
dir_path = os.path.dirname(os.path.realpath(__file__))
lst_img_name = "img_list.csv"
lst_img_dir = os.path.join(dir_path, lst_img_name)
f_result = open(lst_img_dir, mode="r", encoding="utf-8-sig")


class img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.today)

    def __repr__(self):
        return f'<Pic {self.id}>'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/nhentai')
def nhentai():
    return render_template('blank.html')


@app.route('/anilist')
def anilist():
    return render_template('blank.html')


@app.route('/about')
def about():
    return render_template('blank.html')


"""REDDIT SECTION"""


@app.route('/reddit', methods=['POST', 'GET'])
def reddit():
    if request.method == 'POST':
        pic_content = request.form['content']
        new_pic = img(content=pic_content)

        try:
            db.session.add(new_pic)
            db.session.commit()
            return redirect('/reddit')
        except:
            return "There was an issue adding your pic"
    else:
        pics = img.query.order_by(img.date_created).all()
        return render_template('reddit.html', pics=pics)


@app.route('/reddit/update')
def reddit_update():
    update_reddit()

    return redirect('/reddit')


@app.route('/reddit/delete_all')
def delete_all():
    id_list = []

    id_list = get_all_pic_id()

    for id in id_list:
        pic_to_delete = img.query.get_or_404(id)

        try:
            db.session.delete(pic_to_delete)
            db.session.commit()
        except:
            return f'There was a problem deleting this pic: {id}'

    return redirect('/reddit')


@app.route('/view/<int:id>')
def view(id):
    pic = img.query.get_or_404(id)

    try:
        db.session.commit()
        return render_template('view.html', pic=pic)
    except:
        return 'There was a problem open that pic'


@app.route('/delete/<int:id>')
def delete(id):
    pic_to_delete = img.query.get_or_404(id)

    try:
        db.session.delete(pic_to_delete)
        db.session.commit()
        return redirect('/reddit')
    except:
        return 'There was a problem deleting that pic'


@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    pic = img.query.get_or_404(id)

    if request.method == 'POST':
        pic.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/reddit')
        except:
            return 'There was an issue updating your pic'
    else:
        return render_template('update.html', pic=pic)


"""GALLERY SECTION"""


@app.route('/gallery')
def gallery():
    pics = img.query.order_by(img.id).all()
    return render_template('gallery.html', pics=pics)


def get_all_pic_id():
    pics = img.query.all()

    id_list = []

    for pic in pics:
        id = pic.id
        id_list.append(id)
        # print(f"Pic id: {id}")

    return id_list


def update_reddit():
    id_list = []

    id_list = get_all_pic_id()

    for line in f_result:
        ignore_flag = False

        new_pic = line.strip()
        # print(f"Pic content: {id}")
        for id in id_list:
            pic_in_list = img.query.get_or_404(id).content
            if new_pic == pic_in_list:
                ignore_flag = True
                pass

        if ignore_flag == False:
            print(f"--Adding new pic--{new_pic}")
            new_pic_content = img(content=new_pic)
            try:
                db.session.add(new_pic_content)
                db.session.commit()
            except:
                return "There was an issue adding new pics"


@app.route('/gallery/update')
def gallery_update():
    update_reddit()

    return redirect('/gallery')


def check_deleted():
    count = 0
    id_list = []

    id_list = get_all_pic_id()

    print("--Start checking--")

    for pic_id in id_list:
        deleted_flag = False

        pic = img.query.get_or_404(pic_id)

        pic_url = pic.content

        deleted_flag = check_deleted_img(pic_url)

        if deleted_flag == True:
            try:
                pic_to_delete = pic

                db.session.delete(pic_to_delete)
                db.session.commit()

                count += 1
                print(f"--Delete pic--{pic_url}")

                # return redirect('/gallery/check_deleted')
            except:
                return 'There was a problem deleting that pic'
        else:
            print(f"--Pass--{pic_url}")

    print("\nFinish scanning!")

    print(f"{count} picture has been deleted\n")


@app.route('/gallery/check_deleted')
def gallery_check_deleted():
    check_deleted()

    return redirect('/gallery')


if __name__ == "__main__":
    app.run(debug=True)
