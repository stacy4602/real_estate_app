from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory data structures to store users and properties
users = {}
properties = {}
property_id_counter = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.get(email)
        if user and user['password'] == password:
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    global users
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        if email in users:
            return 'Email already registered', 400
        users[email] = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email,
            'password': password,
            'role': role
        }
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    user_properties = [prop for prop in properties.values() if prop['email'] == user['email']]
    return render_template('dashboard.html', properties=user_properties)

@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    global properties, property_id_counter
    if 'user' not in session or session['user']['role'] != 'seller':
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']
        properties[property_id_counter] = {
            'id': property_id_counter,
            'title': title,
            'description': description,
            'price': price,
            'location': location,
            'email': session['user']['email']
        }
        property_id_counter += 1
        return redirect(url_for('dashboard'))
    return render_template('property_form.html', form_action='add')

@app.route('/edit_property/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):
    if 'user' not in session or session['user']['role'] != 'seller':
        return redirect(url_for('login'))
    property = properties.get(property_id)
    if not property or property['email'] != session['user']['email']:
        return 'Unauthorized', 403
    if request.method == 'POST':
        property['title'] = request.form['title']
        property['description'] = request.form['description']
        property['price'] = request.form['price']
        property['location'] = request.form['location']
        return redirect(url_for('dashboard'))
    return render_template('property_form.html', form_action='edit', property=property)

@app.route('/delete_property/<int:property_id>')
def delete_property(property_id):
    if 'user' not in session or session['user']['role'] != 'seller':
        return redirect(url_for('login'))
    property = properties.get(property_id)
    if not property or property['email'] != session['user']['email']:
        return 'Unauthorized', 403
    del properties[property_id]
    return redirect(url_for('dashboard'))

@app.route('/properties')
def property_list():
    filter_location = request.args.get('filter', '')
    filtered_properties = [prop for prop in properties.values() if filter_location.lower() in prop['location'].lower()]
    return render_template('property_list.html', properties=filtered_properties, filter=filter_location)

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    property = properties.get(property_id)
    if not property:
        return 'Property not found', 404
    return render_template('property_list.html', properties=[property])

@app.route('/interested/<int:property_id>', methods=['POST'])
def interested(property_id):
    if 'user' not in session or session['user']['role'] != 'buyer':
        return redirect(url_for('login'))
    property = properties.get(property_id)
    if not property:
        return 'Property not found', 404
    seller_email = property['email']
    seller = users[seller_email]
    return render_template('interested.html',sellere =seller)
if __name__ == '__main__':
    app.run(debug=True)
