{
    'name': 'Task Management',
    'version': '17.0.1.0.0',
    'summary': 'Simple and beautiful task management',
    'category': 'Productivity',
    'author': 'Tibebu IT',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/task_views.xml',
        'views/task_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
