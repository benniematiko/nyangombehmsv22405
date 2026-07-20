from django.contrib import admin
from django.apps import apps

# Auto-register all models in expense app
models = apps.get_app_config('expense').get_models()
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass