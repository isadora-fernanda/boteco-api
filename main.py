import os

from backend.apis.api import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
