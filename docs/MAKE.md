# Make · Flujo manual por lote

La configuración completa, incluidos entradas, filtros, rutas de recuperación, mapeos de Drive, pruebas por operación y errores, está en [Integración paso a paso](../INTEGRACION_PASO_A_PASO.md#3-conectá-make-y-drive).

El flujo valida el JSON y ejecuta el lote una sola vez. Conserva `batch_id` y `runId` para recuperar archivos del mismo Run si falla una descarga o una subida. Se dejó una guía módulo por módulo porque la compatibilidad de un blueprint depende de las conexiones y la configuración efectiva de Make. La prueba con cuentas y la exportación de ese escenario quedan pendientes.
