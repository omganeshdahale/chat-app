# Chat app
Chat app in Django

LINK: https://djangochat.live

## Getting started
### Requirements
 - Python 3.6+
 - PIP
 - venv
 - Redis

### Installation
```
# Clone the repository
git clone https://github.com/omganeshdahale/chat-app.git

# Enter into the directory
cd chat-app/

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Apply migrations.
python manage.py migrate
```
### Configuration
Create `.env` file in cwd and add the following
```
SECRET_KEY=''
DEBUG=True

EMAIL_USER=''
EMAIL_PASS=''
```
```
# Create a superuser account (follow the prompts afterwards)
python manage.py createsuperuser
```
### Starting the application
```
python manage.py runserver
```
### Starting redis server
```
redis-server
```
