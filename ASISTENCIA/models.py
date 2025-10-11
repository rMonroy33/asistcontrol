from django import models

class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    num_control = models.CharField(max_length=20, unique=True, help_text="Número de control del alumno")

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.num_control})"
    
class Asistencia(models.Model):
    nom_alumno = models.ForekignKey(Alumno, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    hora_entrada = models.TimeField(auto_now_add=True)

    class Meta:
        # Solo una entrada por día por alumno
        unique_together = ('nom_alumno', 'fecha')
        ordering = ['-fecha', 'hora_entrada']

    def __str__(self):
        return f"Asistencia de {self.alumno.nombre} el {self.fecha})"
    
