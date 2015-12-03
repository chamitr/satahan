__author__ = 'Chamit'

import os
import socket
from satahan import app

if socket.gethostname() == 'BFF':
    app.run(debug=True, threaded=True)
