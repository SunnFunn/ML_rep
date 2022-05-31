from app import app

if __name__ == '__main__':
    app.run(host=Config.MODEL_HOST, port=Config.MODEL_PORT)
