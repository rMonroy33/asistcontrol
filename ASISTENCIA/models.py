from django.db import models

class Alumno(models.Model):
    nombre = models.CharField(max_length=150)
    carrera = models.CharField(max_length=100)
    num_control = models.CharField(max_length=20, unique=True, help_text="Código único del alumno")

    def __str__(self):
        return f"{self.nombre} {self.carrera} ({self.num_control})" 
    
class Asistencia(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    hora_entrada = models.TimeField(auto_now_add=True)

    class Meta:
        unique_together = ('alumno', 'fecha')
        ordering = ['-fecha', '-hora_entrada']

    def __str__(self):
        return f"Asistencia de {self.alumno.nombre} el {self.fecha} a las {self.hora_entrada}"
