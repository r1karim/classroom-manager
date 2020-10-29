from classroom_manager import socketio,app

if __name__ == "__main__":
    socketio.run(app, debug=True,host='0.0.0.0', port=5000)