# PROC-01 · Cambiar el estado de un job sin usar Kill

Contenido de ejemplo, escrito para el curso. No corresponde a ningún cliente.

Cuando un job queda en estado Executing más tiempo del esperado, primero se revisa su log de salida para confirmar si el proceso sigue vivo en el agente.

Si el proceso ya terminó en el servidor pero Control-M no lo registró, se puede marcar el job como Set to OK. Esta acción no detiene ningún proceso: solo cambia el estado en Control-M.

Antes de usar Set to OK se debe dejar registro en el ticket del motivo y de quién lo aprobó. Es una acción de impacto controlado.

No se debe usar Kill sobre un job cuyo proceso ya terminó, porque no hay nada que detener y se pierde la trazabilidad.
