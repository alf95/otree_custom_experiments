from os import environ

use_bot_ug = eval(environ.get('USE_BOT_UG')) if environ.get('USE_BOT_UG') is not None else False

SESSION_CONFIGS = [
    dict(
        name='public_goods_simple',
        display_name="Public Goods Game",
        num_demo_participants=3,
        app_sequence=['public_goods_simple', 'payment_info'],
        endowment_default=40,
        MPCR=0.5
    ),
    dict(
        name='ultimatum_game',
        display_name="Ultimatum Game",
        app_sequence=['ultimatum_game', 'payment_info'],
        num_demo_participants=2,
        use_browser_bots=use_bot_ug
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as session.config,
# e.g. session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
        use_secure_urls=True
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),

    dict(
        name='test',
        display_name='Test class (same file)',
        participant_label_file='_rooms/econ101.txt',
        use_secure_urls=True
    ),
    dict(
        name='test_60_pl',
        display_name='Test 60 players',
        participant_label_file='_rooms/test_60players.txt',
        use_secure_urls=True
    )
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""

# don't share this with anybody.
SECRET_KEY = '6lertt4wlb09zj@4wyuy-p-6)i$vh!ljwx&r9bti6kgw54k-h8'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

# inactive session configs
