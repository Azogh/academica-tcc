from django.contrib import admin
from .models import Curso, MatrizCurricular, Disciplinas, Turma, Horario, Usuario

admin.site.register(Usuario)
admin.site.register(Curso)  # <--- Importante para aparecer no painel
admin.site.register(MatrizCurricular)
admin.site.register(Disciplinas)
admin.site.register(Turma)
admin.site.register(Horario)