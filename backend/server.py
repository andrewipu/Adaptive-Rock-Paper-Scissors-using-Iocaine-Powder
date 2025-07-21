from flask import Flask
from flask_cors import CORS # Need to handle/enable Cross-Origin Resource Sharing (CORS) to allow requests from React frontend.

app = Flask(__name__)
CORS(app) # Enable CORS for my Flask app


@app.route("/api/play", methods=["POST"])
def play_game():
    # As this is a mock, ignore player's move and always return  the same result.
    dummy_result = {
        "player_move": "rock",
        "computer_move": "scissors",
        "result": "win"
    }
    return dummy_result

# What's the point of this code?
# if __name__ == '__main__':
#     app.run(debug=True)