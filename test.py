from flask import Flask, request
import time
app = Flask(__name__)


@app.route('/hello')
def hello_name():
    name = request.args.get('name','')
    return 'hello' + name + '!'


if __name__ == '__main__':
    app.run()
