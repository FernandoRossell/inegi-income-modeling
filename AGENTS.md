# Reglas del proyecto

1. Los notebooks son documentos academicos ejecutables y deben declarar su unidad de analisis.
2. Todo codigo sustantivo especifico de un analisis vive en el notebook correspondiente. No crear ni importar modulos `.py` propios para ocultar preparacion, modelado, diagnosticos, visualizacion o exportacion.
3. Se permiten librerias publicas y funciones pequenas definidas en celdas del propio notebook.
4. No mezclar tablas de distinta granularidad sin justificacion, validacion de cardinalidad y documentacion.
5. Agrupar la particion por hogar no cambia la granularidad persona.
6. Los outputs visibles proceden de objetos creados durante la ejecucion actual; la exportacion va al final.
7. Codex no ejecuta notebooks salvo solicitud explicita de la persona usuaria.
8. Codex no hace push ni merge sin autorizacion explicita.
