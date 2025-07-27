# 📚 API Documentation

This directory contains the OpenAPI specification for the MindMate API.

---

## 🌐 Online Swagger Editor (manual import)

You can also load and view the OpenAPI spec in your browser:

1. Go to: https://editor.swagger.io/
2. Click `File → Import File`
3. Choose `docs/openapi.json`

This gives you an interactive view and lets you edit and test the API live.

---

## 📁 Project Structure

```
docs/
├── README.md             # This file
└── openapi.json      # Auto-generated OpenAPI 3.0 spec
```

---

## 🔄 Exporting from FastAPI

To regenerate the OpenAPI spec from your FastAPI backend:

```bash
curl http://localhost:8000/openapi.json -o docs/openapi.json
```

This keeps your documentation in sync with the backend logic.

---
