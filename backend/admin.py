from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Sum, F

from backend.models import Categoria, Cliente, Proveedor, Producto, Compra, Pedido, Movimiento, TipoChoices


# Register your models here.

class MovimientoCompraInline(admin.TabularInline):
    model = Movimiento
    exclude = ('pedido', 'fecha', 'tipo', 'usuario')
    extra = 0

class MovimientoPedidoInline(admin.TabularInline):
    model = Movimiento
    exclude = ('compra', 'fecha', 'tipo', 'usuario')
    extra = 0

class MovimientoProductoInline(admin.TabularInline):
    model = Movimiento
    exclude = ('fecha',)
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock', 'precio', 'categoria')
    search_fields = ('nombre',)
    list_filter = ('categoria',)
    exclude = ('pedido',)
    inlines = (MovimientoProductoInline,)

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    search_fields = ('proveedor__nombre',)
    list_display = ('proveedor', 'fecha', 'total')
    list_filter = ('proveedor',)
    date_hierarchy = 'fecha'
    inlines = (MovimientoCompraInline,)
    readonly_fields = ('total',)

    def save_related(self, request, form, formset, change):
        super(CompraAdmin, self).save_related(request, form, formset, change)
        movimiento = form.instance.movimiento_set.all()

        if movimiento.exists():
            total = movimiento.aggregate(
                total=Sum(F('cantidad') * F('producto__precio'))
            )['total']

            if total is not None:
                form.instance.total = total
                form.instance.save()

    def save_formset(self, request, form, formset, change):
        try:
            with transaction.atomic():
                # Guardar instancias sin commit para modificar
                instances = formset.save(commit=False)
                stock_updates = {}  # {producto_id: delta}

                # Procesar instancias nuevas o modificadas
                for instance in instances:
                    producto = instance.producto
                    if instance.pk:  # Item existente: calcular diferencia
                        original = Movimiento.objects.get(pk=instance.pk)
                        delta = instance.cantidad - original.cantidad
                    else:  # Nuevo item: restar cantidad
                        delta = instance.cantidad

                    # Acumular cambios en stock
                    if producto.id in stock_updates:
                        stock_updates[producto.id] += delta
                    else:
                        stock_updates[producto.id] = delta

                # Procesar items eliminados: sumar al stock
                for obj in formset.deleted_objects:
                    producto = obj.producto
                    if producto.id in stock_updates:
                        stock_updates[producto.id] -= obj.cantidad
                    else:
                        stock_updates[producto.id] = -obj.cantidad

                # Aplicar cambios al stock usando F() para evitar race conditions
                for producto_id, delta in stock_updates.items():
                    if delta != 0:
                        Producto.objects.filter(id=producto_id).update(
                            stock=F("stock") +  delta
                        )

                # Guardar instancias y eliminar objetos marcados
                for instance in instances:
                    instance.usuario_id = request.user.id
                    instance.tipo = TipoChoices.entrada
                    instance.save()
                formset.save_m2m()
                for obj in formset.deleted_objects:
                    obj.delete()

        except IntegrityError as e:
            if "stock_no_negativo" in str(e):
                messages.error(request, "Stock insuficiente para uno o más productos.")
            else:
                messages.error(request, "Error al guardar.")

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    search_fields = ('cliente__nombre',)
    list_display = ('cliente', 'fecha', 'total')
    list_filter = ('cliente',)
    date_hierarchy = 'fecha'
    inlines = (MovimientoPedidoInline,)
    readonly_fields = ('total',)

    def save_related(self, request, form, formset, change):
        super(PedidoAdmin, self).save_related(request, form, formset, change)
        movimiento = form.instance.movimiento_set.all()

        if movimiento.exists():
            total = movimiento.aggregate(
                total=Sum(F('cantidad') * F('producto__precio'))
            )['total']

            if total is not None:
                form.instance.total = total
                form.instance.save()

    def save_formset(self, request, form, formset, change):
        try:
            with transaction.atomic():
                # Guardar instancias sin commit para modificar
                instances = formset.save(commit=False)
                stock_updates = {}  # {producto_id: delta}

                # Procesar instancias nuevas o modificadas
                for instance in instances:
                    producto = instance.producto
                    if instance.pk:  # Item existente: calcular diferencia
                        original = Movimiento.objects.get(pk=instance.pk)
                        delta = instance.cantidad - original.cantidad
                    else:  # Nuevo item: restar cantidad
                        delta = instance.cantidad

                    # Acumular cambios en stock
                    if producto.id in stock_updates:
                        stock_updates[producto.id] += delta
                    else:
                        stock_updates[producto.id] = delta

                # Procesar items eliminados: sumar al stock
                for obj in formset.deleted_objects:
                    producto = obj.producto
                    if producto.id in stock_updates:
                        stock_updates[producto.id] -= obj.cantidad
                    else:
                        stock_updates[producto.id] = -obj.cantidad

                # Aplicar cambios al stock usando F() para evitar race conditions
                for producto_id, delta in stock_updates.items():
                    if delta != 0:
                        Producto.objects.filter(id=producto_id).update(
                            stock=F("stock") - delta
                        )

                # Guardar instancias y eliminar objetos marcados
                for instance in instances:
                    instance.usuario_id = request.user.id
                    instance.tipo = TipoChoices.salida
                    instance.save()
                formset.save_m2m()
                for obj in formset.deleted_objects:
                    obj.delete()

        except IntegrityError as e:
            if "stock_no_negativo" in str(e):
                messages.error(request, "Stock insuficiente para uno o más productos.")
            else:
                messages.error(request, "Error al guardar.")



