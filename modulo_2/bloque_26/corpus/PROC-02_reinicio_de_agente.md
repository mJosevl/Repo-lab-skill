# PROC-02 · Revisar un agente desconectado

Contenido de ejemplo, escrito para el curso. No corresponde a ningún cliente.

Si un agente aparece como Unavailable, primero se verifica la conectividad entre el servidor de Control-M y el host del agente.

Luego se revisa en el host si los procesos del agente están arriba. Si no lo están, se inician con el usuario dueño de la instalación.

Reiniciar un agente es una acción de impacto alto: los jobs que estaban corriendo en ese host pueden quedar en estado desconocido. Requiere aprobación del responsable del ambiente.

Después del reinicio se confirma que el agente vuelve a Available y que los jobs pendientes retoman su ejecución.
