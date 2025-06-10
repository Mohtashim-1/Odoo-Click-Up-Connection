{
    "name": "ClickUp Integration",
    "version": "17.0.1.0.0",
    "technical_name": "clickup_integration",
    "author": "Mohtashim",
    "category": "Tools",
    "summary": "Integrate ClickUp OAuth2 with Odoo",
    "depends": ["base", 'web','project'],
    # "assets": {
        # "web.assets_backend": [
        #     "clickup_connector/static/src/js/kanban_interactions.js"
        #     "clickup_connector/static/src/css/sidebar.css",
        #     "clickup_connector/static/src/js/kanban_sidebar.js",
    #         "clickup_connector/static/src/js/sidebar.js",
    #         "clickup_connector/static/src/js/sidebar_mount.js",
            # ],
    #     "web.assets_qweb": [
    #         "clickup_connector/static/src/xml/sidebar.xml"
    #         ]
    # },
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        "views/clickup_views.xml",
        "views/clickup_team_views.xml",
        "views/res_users_view.xml",
        'views/clickup_authorization_view.xml',
        'views/clickup_task_views.xml',
        'views/clickup_space_view.xml',
        'views/clickup_list_views.xml',
        'views/clickup_folder_view.xml',
        'views/project_task_view.xml',
        'views/clickup_cron.xml',
        # 'views/project_task_kanban_sidebar.xml'
    ],
    'images': [
            "static/description/cover.png",
            "static/description/icon.png",
    ],
    "installable": True,
    "application": True,
    "license": "MIT",

}
