from django.contrib import admin

from .models import CodeSignToken, CoreSettings, CustomField, Integration

admin.site.register(CoreSettings)
admin.site.register(CustomField)
admin.site.register(CodeSignToken)
admin.site.register(Integration)
