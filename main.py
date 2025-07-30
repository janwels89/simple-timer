import sys
from app.controller import AppController

def main():
    debug = '--debug' in sys.argv
    app = AppController(debug=debug)
    app.run()

if __name__ == '__main__':
    main()