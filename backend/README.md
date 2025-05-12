# 2025-Spring-Capstone

## Cybersecurity AI Assistant Backend

This is the FastAPI backend for the Cybersecurity AI Assistant application. It provides AI-powered analysis and recommendations for cybersecurity queries using LLM technology.

### Features

- AI-powered cybersecurity query processing
- Plugin system for extending functionality
- RESTful API for frontend integration
- SQLAlchemy ORM for database interactions

### Setup Instructions

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key and other configuration

4. **Run the server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

5. **Access the API documentation**:
   - Open your browser and go to `http://localhost:8000/docs`

### API Endpoints

- **GET /**: Health check endpoint
- **GET /api/plugins/**: List all available plugins
- **POST /api/plugins/**: Create a new plugin
- **GET /api/plugins/{plugin_id}**: Get plugin details
- **PUT /api/plugins/{plugin_id}**: Update a plugin
- **DELETE /api/plugins/{plugin_id}**: Delete a plugin
- **POST /api/query/process**: Process a cybersecurity query
- **POST /api/query/recommend-plugins**: Get plugin recommendations for a query

### Database

The application uses SQLAlchemy with SQLite by default. You can configure it to use PostgreSQL or other databases by updating the `DATABASE_URL` in the `.env` file.
