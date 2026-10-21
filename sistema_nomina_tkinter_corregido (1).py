"""
Business Payroll System
Phase 3 - Exercise 3
Desktop interface built with Tkinter.

Demonstrates:
- Abstract base class and abstract method.
- Inheritance and polymorphism.
- Multiple inheritance through the Bonificable mixin.
- Optional parameters in mostrar_informacion().
"""

# Importa Tkinter para construir la interfaz gráfica de escritorio.
import tkinter as tk
# ttk aporta controles mejorados y messagebox muestra avisos al usuario.
from tkinter import ttk, messagebox
# ABC y abstractmethod permiten definir una clase base abstracta.
from abc import ABC, abstractmethod


# Mixin reutilizable: agrega el comportamiento de las bonificaciones.
class Bonificable:
    """Mixin that provides reusable bonus behavior."""

    # Inicializa la bonificación y la convierte a número decimal.
    def __init__(self, bonificacion=0):
        self.bonificacion = float(bonificacion)

    # Devuelve el valor de la bonificación del empleado.
    def calcular_bonificacion(self):
        """Return the employee's bonus amount."""
        return self.bonificacion

    # Cambia la bonificación y evita aceptar cantidades negativas.
    def establecer_bonificacion(self, cantidad):
        """Update the employee's bonus."""
        cantidad = float(cantidad)
        if cantidad < 0:
            raise ValueError("Bonus cannot be negative.")
        self.bonificacion = cantidad


# Clase abstracta común: concentra los datos que comparten los empleados.
class Empleado(ABC):
    """Abstract base class shared by all employee types."""

    # Guarda la información de identificación del empleado.
    def __init__(self, nombre, documento):
        self.nombre = nombre
        self.documento = documento

    # Cada subclase debe implementar su propia fórmula salarial.
    @abstractmethod
    def calcular_salario(self):
        """Calculate the employee's total salary."""
        raise NotImplementedError

    def obtener_tipo(self):
        """Return a readable employee type."""
        return "Employee"

    # Los parámetros opcionales permiten mostrar información básica o ampliada.
    def mostrar_informacion(self, incluir_salario=False,
                            incluir_bonificaciones=False):
        """
        Display basic details by default.
        Optional parameters add total salary and bonus/payroll details.
        """
        datos = [
            f"Name: {self.nombre}",
            f"Document: {self.documento}",
            f"Employee type: {self.obtener_tipo()}",
        ]

        if incluir_salario:
            datos.append(f"Total salary: ${self.calcular_salario():,.2f}")

        if incluir_bonificaciones:
            bonificacion = getattr(self, "bonificacion", 0)
            datos.append(f"Bonus: ${bonificacion:,.2f}")
            # Add subclass-specific payroll details when available.
            if isinstance(self, EmpleadoTiempoCompleto):
                datos.append(f"Monthly salary: ${self.salario_mensual:,.2f}")
            elif isinstance(self, EmpleadoPorHoras):
                datos.append(f"Hours worked: {self.horas_trabajadas:g}")
                datos.append(f"Hourly rate: ${self.valor_hora:,.2f}")
            elif isinstance(self, EmpleadoComision):
                datos.append(f"Base salary: ${self.salario_base:,.2f}")
                datos.append(f"Sales: ${self.ventas:,.2f}")
                datos.append(f"Commission rate: {self.porcentaje_comision:g}%")
                datos.append(f"Commission: ${self.calcular_comision():,.2f}")

        return "\n".join(datos)

    def __str__(self):
        """Return a concise string representation of the employee."""
        return f"{self.nombre} - {self.documento}"


# Herencia múltiple: combina los datos del empleado y el comportamiento Bonificable.
class EmpleadoTiempoCompleto(Empleado, Bonificable):
    """Employee paid a fixed monthly salary plus a bonus."""

    def __init__(self, nombre, documento, salario_mensual, bonificacion=0):
        Empleado.__init__(self, nombre, documento)
        Bonificable.__init__(self, bonificacion)
        self.salario_mensual = float(salario_mensual)

    def calcular_salario(self):
        return self.salario_mensual + self.calcular_bonificacion()

    def obtener_tipo(self):
        return "Full-time"

    def __str__(self):
        return (f"{self.nombre} | Full-time | "
                f"Salary: ${self.calcular_salario():,.2f}")


# El salario por horas se calcula multiplicando horas por tarifa y sumando la bonificación.
class EmpleadoPorHoras(Empleado, Bonificable):
    """Employee paid according to hours worked and hourly rate."""

    def __init__(self, nombre, documento, horas_trabajadas, valor_hora,
                 bonificacion=0):
        Empleado.__init__(self, nombre, documento)
        Bonificable.__init__(self, bonificacion)
        self.horas_trabajadas = float(horas_trabajadas)
        self.valor_hora = float(valor_hora)

    def calcular_salario(self):
        return (self.horas_trabajadas * self.valor_hora
                + self.calcular_bonificacion())

    def obtener_tipo(self):
        return "Hourly"

    def __str__(self):
        return f"{self.nombre} | Hourly | Salary: ${self.calcular_salario():,.2f}"


# El salario por comisión suma salario base, comisión sobre ventas y bonificación.
class EmpleadoComision(Empleado, Bonificable):
    """Employee paid a base salary plus sales commission and bonus."""

    def __init__(self, nombre, documento, salario_base, ventas,
                 porcentaje_comision, bonificacion=0):
        Empleado.__init__(self, nombre, documento)
        Bonificable.__init__(self, bonificacion)
        self.salario_base = float(salario_base)
        self.ventas = float(ventas)
        self.porcentaje_comision = float(porcentaje_comision)

    def calcular_comision(self):
        return self.ventas * (self.porcentaje_comision / 100)

    def calcular_salario(self):
        return (self.salario_base + self.calcular_comision()
                + self.calcular_bonificacion())

    def obtener_tipo(self):
        return "Commission"

    def __str__(self):
        return (f"{self.nombre} | Commission | "
                f"Salary: ${self.calcular_salario():,.2f}")


# Esta clase administra la ventana, los registros y las operaciones de nómina.
class SistemaNomina:
    """Manage employee records and the Tkinter graphical interface."""

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("BUSINESS PAYROLL SYSTEM")
        self.ventana.geometry("1050x700")
        self.ventana.resizable(False, False)
        self.empleados = []
        self.crear_interfaz()

    # Construye los campos, botones, tabla y total de nómina.
    def crear_interfaz(self):
        """Create and arrange all visible interface elements."""
        tk.Label(
            self.ventana, text="BUSINESS PAYROLL SYSTEM",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        frame_principal = tk.Frame(self.ventana)
        frame_principal.pack(fill="both", expand=True, padx=20)

        frame_datos = tk.LabelFrame(
            frame_principal, text="Employee Information",
            font=("Arial", 11, "bold"), padx=15, pady=10
        )
        frame_datos.pack(fill="x")

        tk.Label(frame_datos, text="Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.entrada_nombre = tk.Entry(frame_datos, width=30)
        self.entrada_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_datos, text="Document:").grid(
            row=0, column=2, sticky="w", padx=5)
        self.entrada_documento = tk.Entry(frame_datos, width=25)
        self.entrada_documento.grid(row=0, column=3, padx=5)

        tk.Label(frame_datos, text="Employee type:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.combo_tipo = ttk.Combobox(
            frame_datos,
            values=["Full-time", "Hourly", "Commission"],
            state="readonly", width=27
        )
        self.combo_tipo.grid(row=1, column=1, padx=5, pady=5)
        self.combo_tipo.current(0)
        self.combo_tipo.bind("<<ComboboxSelected>>", self.cambiar_campos)

        self.frame_variables = tk.LabelFrame(
            frame_principal, text="Payroll Information",
            font=("Arial", 11, "bold"), padx=15, pady=10
        )
        self.frame_variables.pack(fill="x", pady=10)

        self.label_campo1 = tk.Label(self.frame_variables, text="Monthly salary:")
        self.label_campo1.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_campo1 = tk.Entry(self.frame_variables, width=25)
        self.entrada_campo1.grid(row=0, column=1, padx=5, pady=5)

        self.label_campo2 = tk.Label(self.frame_variables, text="Bonus:")
        self.label_campo2.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entrada_campo2 = tk.Entry(self.frame_variables, width=25)
        self.entrada_campo2.grid(row=0, column=3, padx=5, pady=5)

        frame_botones = tk.Frame(frame_principal)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Register Employee", width=20,
                  command=self.registrar_empleado).grid(row=0, column=0, padx=5)
        tk.Button(frame_botones, text="Clear", width=15,
                  command=self.limpiar).grid(row=0, column=1, padx=5)
        tk.Button(frame_botones, text="Delete Selected", width=20,
                  command=self.eliminar_empleado).grid(row=0, column=2, padx=5)
        tk.Button(frame_botones, text="View Details", width=15,
                  command=self.ver_detalles).grid(row=0, column=3, padx=5)

        frame_tabla = tk.LabelFrame(
            frame_principal, text="Registered Employees",
            font=("Arial", 11, "bold")
        )
        frame_tabla.pack(fill="both", expand=True, pady=5)

        columnas = ("nombre", "documento", "tipo", "salario", "bonificacion")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings", height=12)
        encabezados = {
            "nombre": "Name", "documento": "Document",
            "tipo": "Employee Type", "salario": "Total Salary",
            "bonificacion": "Bonus"
        }
        anchos = {
            "nombre": 200, "documento": 130, "tipo": 150,
            "salario": 150, "bonificacion": 150
        }
        for columna in columnas:
            self.tabla.heading(columna, text=encabezados[columna])
            self.tabla.column(columna, width=anchos[columna])
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.label_total = tk.Label(
            frame_principal, text="Total Payroll: $0.00",
            font=("Arial", 14, "bold")
        )
        self.label_total.pack(pady=10)

    # Ajusta las etiquetas de entrada según el tipo de empleado seleccionado.
    def cambiar_campos(self, evento=None):
        """Update field labels based on the selected employee type."""
        tipo = self.combo_tipo.get()
        self.entrada_campo1.delete(0, tk.END)
        self.entrada_campo2.delete(0, tk.END)
        if tipo == "Full-time":
            self.label_campo1.config(text="Monthly salary:")
            self.label_campo2.config(text="Bonus:")
        elif tipo == "Hourly":
            self.label_campo1.config(text="Hours worked:")
            self.label_campo2.config(text="Hourly rate:")
        else:
            self.label_campo1.config(text="Base salary:")
            self.label_campo2.config(text="Sales:")

    # Lee los datos del formulario, valida entradas y crea la subclase adecuada.
    def registrar_empleado(self):
        """Validate input and create the selected employee object."""
        nombre = self.entrada_nombre.get().strip()
        documento = self.entrada_documento.get().strip()
        tipo = self.combo_tipo.get()

        if not nombre or not documento:
            messagebox.showwarning(
                "Incomplete Information", "Enter the employee name and document.")
            return
        try:
            campo1 = float(self.entrada_campo1.get())
            campo2 = float(self.entrada_campo2.get())
            if campo1 < 0 or campo2 < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Values", "Enter valid non-negative numeric values.")
            return

        if tipo == "Full-time":
            empleado = EmpleadoTiempoCompleto(nombre, documento, campo1, campo2)
            self._guardar_empleado(empleado)
        elif tipo == "Hourly":
            empleado = EmpleadoPorHoras(nombre, documento, campo1, campo2)
            self._guardar_empleado(empleado)
        else:
            self._solicitar_comision(nombre, documento, campo1, campo2)

    # Centraliza el guardado para actualizar la tabla y limpiar el formulario.
    def _guardar_empleado(self, empleado):
        """Add an employee, refresh the table and confirm the operation."""
        self.empleados.append(empleado)
        self.actualizar_tabla()
        self.limpiar()
        messagebox.showinfo(
            "Employee Registered", "The employee was registered successfully.")

    # La comisión requiere un porcentaje adicional, solicitado en una ventana secundaria.
    def _solicitar_comision(self, nombre, documento, salario_base, ventas):
        """Open a small dialog to request the commission percentage."""
        ventana_comision = tk.Toplevel(self.ventana)
        ventana_comision.title("Commission Rate")
        ventana_comision.geometry("350x180")
        ventana_comision.resizable(False, False)

        tk.Label(
            ventana_comision, text="Enter the commission percentage:",
            font=("Arial", 11)
        ).pack(pady=15)
        entrada_porcentaje = tk.Entry(ventana_comision, width=20)
        entrada_porcentaje.pack()

        # Valida el porcentaje y registra al empleado comisionista.
        def guardar_comision():
            try:
                porcentaje = float(entrada_porcentaje.get())
                if porcentaje < 0:
                    raise ValueError
                empleado = EmpleadoComision(
                    nombre, documento, salario_base, ventas, porcentaje)
                self.empleados.append(empleado)
                self.actualizar_tabla()
                ventana_comision.destroy()
                self.limpiar()
                messagebox.showinfo(
                    "Employee Registered",
                    "The employee was registered successfully.")
            except ValueError:
                messagebox.showerror(
                    "Invalid Value", "Enter a valid non-negative percentage.")

        tk.Button(
            ventana_comision, text="Register", command=guardar_comision,
            width=15
        ).pack(pady=20)

    # Vuelve a dibujar la tabla y suma los salarios de todos los empleados.
    def actualizar_tabla(self):
        """Refresh the employee table and calculate the payroll total."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for empleado in self.empleados:
            bonificacion = getattr(empleado, "bonificacion", 0)
            self.tabla.insert(
                "", tk.END,
                values=(
                    empleado.nombre, empleado.documento, empleado.obtener_tipo(),
                    f"${empleado.calcular_salario():,.2f}",
                    f"${bonificacion:,.2f}"
                )
            )
        total = sum(e.calcular_salario() for e in self.empleados)
        self.label_total.config(text=f"Total Payroll: ${total:,.2f}")

    # Elimina solo el registro seleccionado, después de pedir confirmación.
    def eliminar_empleado(self):
        """Delete the selected employee after confirmation."""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning(
                "No Selection", "Select an employee first.")
            return
        indice = self.tabla.index(seleccionado[0])
        empleado = self.empleados[indice]
        confirmar = messagebox.askyesno(
            "Confirm Deletion", f"Do you want to delete {empleado.nombre}?")
        if confirmar:
            del self.empleados[indice]
            self.actualizar_tabla()

    # Presenta los datos ampliados usando los parámetros opcionales del método.
    def ver_detalles(self):
        """Show full details using the optional information parameters."""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning(
                "No Selection", "Select an employee first.")
            return
        indice = self.tabla.index(seleccionado[0])
        empleado = self.empleados[indice]
        detalles = empleado.mostrar_informacion(
            incluir_salario=True, incluir_bonificaciones=True)
        messagebox.showinfo("Employee Details", detalles)

    # Restablece los campos del formulario y selecciona el tipo predeterminado.
    def limpiar(self):
        """Clear input fields and restore the default employee type."""
        self.entrada_nombre.delete(0, tk.END)
        self.entrada_documento.delete(0, tk.END)
        self.entrada_campo1.delete(0, tk.END)
        self.entrada_campo2.delete(0, tk.END)
        self.combo_tipo.current(0)
        self.cambiar_campos()


if __name__ == "__main__":
    # Create the main window and start the Tkinter event loop.
    ventana = tk.Tk()
    app = SistemaNomina(ventana)
    ventana.mainloop()
