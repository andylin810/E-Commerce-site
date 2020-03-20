# About this project
This is a basic E-commerce site which includes the following functionalities:

* Login/Logout
* Creating Account
* Viewing Products
* Uploading Products
* Buying Product/Receiving Payment through Stripe

# Screenshots of the site

This site is developed using the Django framework. All of the Django views were coded using functional based Django views for learning purposes for me to understand better how Django works, however they will be changed to Django's class based views for code efficiency later. Also, SQLite is the local story database that is being used by this site, it will and should be changed to other database such as PostgreSQL, the Stripe key should also be changed to your own accordingly to test for payments in settings.py
.
The site is still in development, and it will have more functionalities implemented and it will also receive more UI polishing.

# To run the project

1. Clone the project
```
git clone https://github.com/andylin810/E-Commerce-site.git
```
2. Create and start a python virtual environment
```
$ pip install virtualenv
$ virtualenv django-web
$ source django-web/bin/activate
```
3. Install dependencies for the project
```
$ pip install -r requirements.txt
```

4. Creating Admin account to access database
```
$ python manage.py createsuperuser
```

5. Start the server
```
$ python manage.py runserver
```
Visit http://127.0.0.1:8000/login/products/ to see the main page.
