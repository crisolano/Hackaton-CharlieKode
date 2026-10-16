# Sistema Central de Gestión Operativa del Campus

Hackatón Campuslands — "El campus bajo presión".

## Requisitos y Puesta en Marcha
1. **Crear y activar entorno virtual:**
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Variables de entorno:**
   ```powershell
   copy .env.example .env
   ```
4. **Ejecutar servidor local:**
   ```powershell
   uvicorn app.main:app --reload
   ```
   - Aplicación: http://localhost:8000
   - Documentación Swagger: http://localhost:8000/docs
   - Endpoint de salud: http://localhost:8000/health

5. **Pruebas y calidad de código:**
   ```powershell
   pytest
   ruff check .
   ruff format .
   ```