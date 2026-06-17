# llm-note

**llm-note** es un motor local de notas para agentes LLM. Combina un registro SQLite con cuadernos de texto plano sin servicios alojados ni dependencias de ejecución externas.

## Funciones

- Guardar notas, entradas de diario, categorías, estados de ánimo y marcas de promoción.
- Mantener cuadernos portables de texto plano.
- Buscar notas desde Python o la CLI.
- Crear entradas de lluvia de ideas para convertirlas después en tareas, páginas wiki o issues.
- Incluir mensajes de usuario en seis idiomas.

## Inicio rápido

```bash
pip install -e .
llm-note --locale es write "Revisar privacidad antes del release" --cat release
llm-note --locale es search privacidad
```

## Licencia

[MIT](LICENSE)
