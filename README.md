chat_app/
│
├── chat_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/
│   ├── migrations/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── chat/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── consumers.py
│   ├── routing.py
│   └── urls.py
│
├── templates/
│   ├── accounts/
│   │   ├── register.html
│   │   └── login.html
│   │
│   └── chat/
│       ├── user_list.html
│       └── chat.html
│
├── db.sqlite3
├── manage.py
└── README.md