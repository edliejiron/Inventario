from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class  Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorias"
        verbose_name = "Categoria"


class TipoChoices(models.IntegerChoices):
    entrada = 1, 'Entrada'
    salida = 2, 'Salida'



class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name_plural = "Proveedores"
        verbose_name = "Proveedor"

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Clientes"
        verbose_name = "Cliente"

class Pedido(models.Model):
    fecha = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.cliente.nombre}'

    class Meta:
        verbose_name_plural = "Pedidos"
        verbose_name = "Pedido"


class Compra(models.Model):
    fecha = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.proveedor.nombre}'

    class Meta:
        verbose_name_plural = "Compras"
        verbose_name = "Compra"


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.FloatField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Productos"
        verbose_name = "Producto"
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name="stock_no_negativo"
            )
        ]

class Movimiento(models.Model):
    tipo = models.IntegerField(max_length=100, choices=TipoChoices.choices)
    cantidad = models.IntegerField()
    fecha = models.DateField(auto_now_add=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, null=True)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return  f'{self.cantidad}'

    class Meta:
        verbose_name_plural = "Movimientos"
        verbose_name = "Movimiento"


