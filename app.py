from config import PORT

import handler
from loader import app
from threading import Thread
from utils.init_swagger import init_swagger

if __name__ == '__main__':
    swag = init_swagger(app)
    app.run(host="0.0.0.0", port=PORT)
