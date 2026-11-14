# Taller-Final_Desarrollo

Diagnóstico Técnico del Sistema

A. Identificación de los principios SOLID incumplidos

1. Principio de Responsabilidad Única (SRP)

En el código proporcionado este principio se incumple principalmente en el archivo routers/checkout.py, específicamente en la función process_checkout().

Esto se debe a que la función concentra demasiadas responsabilidades, pues administra las transacciones de inventario, calcula el valor de la compra, procesa los pagos, genera los documentos de facturación,  coordina el envío de notificaciones y se encarga de manejar las respuestas y excepciones HTTP.

2. Principio Abierto/Cerrado (OCP)

Su incumplimiento se evidencia en services/notification_core.py, particularmente en el método send_alerts(), ya que la selección del canal de notificación depende de una estructura de condiciones (if/elif) que identifica si se debe enviar un correo electrónico, un SMS o un webhook. Lo que significa que, para incorporar un nuevo canal de comunicación, sería necesario modificar directamente el código existente.

3. Principio de Inversión de Dependencias (DIP)

En el proyecto original, este principio se incumple en varios componentes:

TransactionManager depende directamente de db_instance, una instancia concreta de la base de datos definida en database/connection.py.

StripePaymentGateway utiliza directamente la biblioteca requests para comunicarse con el servicio de pagos.

Y en routers/checkout.py, donde se crean directamente las instancias de TransactionManager, StripePaymentGateway, InvoiceGenerator y NotificationDispatcher.

Este diseño genera un fuerte acoplamiento, dificulta la sustitución de servicios y complica la implementación de pruebas unitarias.

4. Principio de Sustitución de Liskov (LSP) e Interfaz Segregada (ISP)

En el código no se identifican incumplimientos directos o de alto impacto sobre la aplicación, debido a que no existen jerarquías de herencia ni interfaces explícitas que permitan evaluar su aplicación.

B. Impacto de las operaciones síncronas bloqueantes en el Event Loop

FastAPI utiliza programación asíncrona para atender múltiples solicitudes de manera eficiente, para ello, normalmente se trabaja con un Event Loop, encargado de coordinar la ejecución de las tareas y permitir que una operación espere por otra sin detener innecesariamente todo el procesamiento.

Sin embargo, en el código original existen operaciones síncronas y bloqueantes dentro de funciones que forman parte de este entorno asíncrono.

Uno de los principales problemas se encuentra en database/session_manager.py, donde se utiliza time.sleep(0.5) dentro del método begin_transaction(), pues esta instrucción detiene la ejecución del hilo durante medio segundo, impidiendo que el Event Loop atienda otras tareas mientras se encuentra bloqueado.

Otro problema aparece en services/payment_service.py, donde se utiliza requests.post() para realizar solicitudes HTTP de manera síncrona, que a pesar de que la petición tiene un tiempo de espera de cinco segundos, durante su ejecución el Event Loop no puede continuar atendiendo otras operaciones.

Asimismo, en services/document_service.py, el método generate_pdf_manifest() ejecuta un cálculo intensivo de CPU que realiza cinco millones de iteraciones, cosa que al ejecutarse directamente dentro de una ruta asíncrona también puede bloquear el hilo que atiende las solicitudes.

En conjunto, estas operaciones provocan un aumento de la latencia, disminuyen la capacidad de respuesta del servidor y pueden ocasionar que múltiples solicitudes permanezcan esperando, incluso cuando algunas de ellas no necesitan utilizar los recursos que están bloqueados.

C. Análisis matemático del comportamiento del inventario bajo alta concurrencia

El sistema original presenta una condición de carrera (Race Condition) en la administración del inventario, debido a que las operaciones de consulta, validación y actualización de existencias no se ejecutan de manera atómica. Esto permite que varias solicitudes simultáneas accedan al mismo valor del inventario antes de que alguna de ellas registre los cambios correspondientes.

Matemáticamente, el inventario final debería calcularse mediante la siguiente expresión:

Sfinal = Sinicial - Sumatoria de Qi de 1 hasta n

Donde Qi es la cantidad solicitada en cada transacción y n el número de transacciones aprobadas.

El problema surge porque el método begin_transaction() obtiene el inventario disponible y verifica si es suficiente antes de realizar su actualización, de forma que drante este intervalo otras solicitudes pueden consultar exactamente el mismo valor inicial y superar igualmente la validación, para que posteriormente cada operación calcula el nuevo inventario utilizando información que puede haber quedado desactualizada.

Como consecuencia, las actualizaciones pueden sobrescribirse entre sí, provocando que el sistema registre una disminución de existencias inferior a la cantidad realmente vendida, lo que genera inconsistencias entre las transacciones aprobadas y el inventario almacenado y permite que se procesen compras que superen las existencias disponibles.
