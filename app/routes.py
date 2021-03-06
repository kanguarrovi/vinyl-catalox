import pdfkit
import datetime
from app import app, db
from flask import render_template, request, redirect, url_for, make_response
from .models import Vinyl
from .forms import AlbumForm

@app.route('/')
@app.route('/index')
def index():
	albums = Vinyl.query.filter_by(status='Available').order_by(Vinyl.artist).order_by(Vinyl.name).all()
	if len(albums) > 0:
		return render_template('index.html', albums=albums)
	else:
		msg = 'No Articles found'
		return render_template('index.html', msg=msg)

@app.route('/add_album', methods=['GET', 'POST'])
def add_album():
	form = AlbumForm(request.form)

	if request.method == 'POST' and form.validate():
		artist = form.artist.data
		name = form.name.data
		price = form.price.data
		status = form.status.data
		info = form.info.data

		album = Vinyl(artist = artist, name = name, price = price, status=status, info=info)
		db.session.add(album)
		db.session.commit()

		return redirect(url_for('dashboard'))
	return render_template('album_form.html', action="Add", form = form)

@app.route('/dashboard')
def dashboard():
	albums = Vinyl.query.order_by(Vinyl.artist).order_by(Vinyl.name).all()
	if len(albums) > 0:
		return render_template('dashboard.html', albums = albums)
	else:
		msg = 'No Articles found'
		return render_template('dashboard.html', msg = msg)

@app.route('/edit_album/<string:id>', methods=['GET', 'POST'])
def edit_album(id):
	album = Vinyl.query.get(id)

	#Get form
	form = AlbumForm(request.form)

	#Populate album form fields
	form.artist.data = album.artist
	form.name.data = album.name
	form.price.data = album.price
	form.status.data = album.status
	form.info.data = album.info

	if request.method == 'POST' and form.validate():

		album.artist = request.form['artist']
		album.name = request.form['name']
		album.price = request.form['price']
		album.status = request.form['status']
		album.info = request.form['info']

		db.session.commit()

		return redirect(url_for('dashboard'))

	return render_template('album_form.html', action="Info", form = form)

@app.route('/delete_album/<string:id>', methods=['POST'])
def delete_album(id):
	album = Vinyl.query.get(id)
	db.session.delete(album)
	db.session.commit()
	return redirect(url_for('dashboard'))

@app.route('/gen_list')
def pdf_template():
	options = {
		'page-size': 'A4',
		'margin-top': '0.75in',
		'margin-right': '0.75in',
		'margin-bottom': '0.75in',
		'margin-left': '0.75in',
	}

	albums = Vinyl.query.filter_by(status='Available').order_by(Vinyl.artist).order_by(Vinyl.name).all()
	
	date = datetime.datetime.now()

	date_doc = date.strftime("%Y-%m-%d %H:%M:%S")

	rendered = render_template('pdf_format.html', albums=albums, date=date_doc)
	pdf = pdfkit.from_string(rendered, False, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'

	name = "catalox-list-" + date.strftime("%Y-%m-%d-%H-%M-%S") + ".pdf"
	response.headers['Content-Disposition'] = 'attachment; filename=%s' % name
	return response
