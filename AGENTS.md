# Reglas del proyecto

1. Los notebooks son documentos academicos ejecutables y deben declarar su unidad de analisis.
2. Todo codigo sustantivo especifico de un analisis vive en el notebook correspondiente. No crear ni importar modulos `.py` propios para ocultar preparacion, modelado, diagnosticos, visualizacion o exportacion.
3. Se permiten librerias publicas y funciones pequenas definidas en celdas del propio notebook.
4. No mezclar tablas de distinta granularidad sin justificacion, validacion de cardinalidad y documentacion.
5. Agrupar la particion por hogar no cambia la granularidad persona.
6. Los outputs visibles proceden de objetos creados durante la ejecucion actual; la exportacion va al final.
7. Codex no ejecuta notebooks salvo solicitud explicita de la persona usuaria.
8. Codex no hace push ni merge sin autorizacion explicita.
9. En comparaciones temporales, conservar el target nominal y documentar el factor usado para expresarlo en pesos de 2024; no alterar marts.
10. Los años ENIGH son cortes transversales, no seguimiento de personas u hogares. No trasladar selecciones exploratorias de un año a otro automaticamente.
