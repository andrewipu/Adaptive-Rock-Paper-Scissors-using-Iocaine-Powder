from flask import Flask, request, jsonify
from flask_cors import CORS  # Need to handle/enable Cross-Origin Resource Sharing (CORS) to allow requests from React frontend.
from iocaine_powder.IocainePowder import IocaineBot

# Initialize Flask app and IocaineBot
app = Flask(__name__)
CORS(app)  # Enable CORS for my Flask app

#Instantiate the IocaineBot.
bot = IocaineBot(trials=50)

# Map integer moves to string representations
move_map = {
    0: "rock",  # 0 represents rock
    1: "paper",  # 1 represents paper
    2: "scissors"  # 2 represents scissors
}

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json() # This is the line that will receive the JSON data from the React frontend.
    user_move = data.get('move') # Get the user's move from the request data - e.g., "rock", "paper", or "scissors".

    #convert string move to integer
    rev_move_map = {v: k for k, v in move_map.items()}  # Reverse the move_map to convert string to integer
    user_move_int = rev_move_map.get(user_move) # Convert the user's move to an integer

    # Check if the user's move is valid, else return an error response
    if user_move_int is None:
        return jsonify({"error": "Invalid move"}), 400
    
    # Get the bot's move
    bot_move_int = bot.get_move()

    # Update the bot's history with the user's move and the bot's move
    bot.update_history(my_move=bot_move_int, opp_move=user_move_int)

    bot_move_str = move_map.get(bot_move_int, 'unknown')  # Convert the bot's move back to a string

    return jsonify({'bot_move':bot_move_str})

@app.route('/reset', methods=['POST'])
def reset():
    global bot
    # Calculate stats from current bot instance
    final_stats = bot.calculate_stats()
     # Reset the bot's state 
    bot = IocaineBot(trials=50)
    # return jsonify({'message': 'Game reset successfully'})
    # Return the calculated stats of the game that just ended
    return jsonify(final_stats) 

if __name__ == '__main__':
    app.run(debug=True)
    