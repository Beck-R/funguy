# Funguy

# Installation:

First, you will need to setup a virtual environment using `python3 -m venv <venv>`.
After that, you will need to activate said virtual environment using `source <venv>/bin/activate`.
After you have done this you will need to install the neseccary dependencies using `pip3 install -r requirements.txt`.
You should also create a django superuser by running `sudo docker-compose run web python manage.py createsuperuser`.

# Usage:

To run the backend server all you need to do is run `sudo docker-compose up`
The server will start on [http://0.0.0.0:8000/](http://0.0.0.0:8000/)

# Development:

After making changes to the database, you must always run `sudo docker-compose run web python manage.py makemigrations`,
followed by `sudo docker-compose run web python manage.py migrate`.

To use run manage.py commands use: `sudo docker-compose run web python manage.py <command>`.
