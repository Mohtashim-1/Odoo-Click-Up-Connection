{
    "name": "ClickUp Integration",
    "version": "1.0",
    "technical_name": "clickup_integration",
    "author": "Mohtashim",
    "category": "Tools",
    "summary": "Integrate ClickUp OAuth2 with Odoo",
    "depends": ["base"],
    "data": [
        'security/security.xml',
        "views/clickup_views.xml",
        "views/res_users_view.xml",
        'views/clickup_authorization_view.xml',
    ],
    "installable": True,
    "application": True,
}
