{
    'name': 'Mantenimiento Ficha Tecnica',
    'version': '1.0',
    'summary': 'Ficha Tecnica Creacion de Recetas',
    'description': 'Modulo mantenimiento de ficha tecnica creacion de recetas',
    'author': 'MarcoAG',
    'depends': ['base', 'web'],
    'data': [
        'views/receta_model_views.xml',
        'views/copia_rec_model_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'receta_dev/static/src/css/style.css'
        ],
    },
    'installable': True,
    'application': True,
}