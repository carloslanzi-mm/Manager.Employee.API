# from gevent.pywsgi import WSGIServer
# from app import APP
#
# http_server = WSGIServer(('0.0.0.0', 5000), APP)
# http_server.serve_forever()

import os
from gevent.pywsgi import WSGIServer
from app import APP


def run_server():
    env = os.getenv("FLASK_ENV", "production")  # Default para produção se não for definido

    if env == "development":
        print("🚀 Running in development mode with auto-reload enabled...")
        APP.run(debug=True, host="0.0.0.0", port=5000)
    else:
        print("🟢 Running in production mode with Gevent...")
        http_server = WSGIServer(("0.0.0.0", 5000), APP)
        http_server.serve_forever()


if __name__ == "__main__":
    run_server()
