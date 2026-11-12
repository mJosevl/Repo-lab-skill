# PROC-03 · Ubicar el Order ID de un job

Contenido de ejemplo, escrito para el curso. No corresponde a ningún cliente.

El Order ID identifica una ejecución específica de un job dentro del día de Control-M. Un mismo job puede tener varios Order ID si se ordenó más de una vez.

Para ubicarlo se busca el job por nombre en la vista de monitoreo y se revisan sus propiedades.

El Order ID es necesario para relanzar, revisar el log o cambiar el estado de una ejecución puntual, sin afectar otras ejecuciones del mismo job.

Es una consulta sin impacto: no modifica nada en el ambiente.
