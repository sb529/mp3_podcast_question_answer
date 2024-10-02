from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = {}  # Stores room data
players_in_rooms = {}

def generate_room_code():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def create_room(data):
    print("Create room event received with data:", data)  # Debug log to check if the event reaches the backend
    
    room_code = generate_room_code()  # Function to generate unique room code
    host_name = data['hostName']
    num_players = data['players']
    
    room_info = {
        'host': host_name,
        'players': [host_name],
        'num_players': int(num_players),
        'rounds': data['rounds'],
        'time_per_round': data['time'],
        'customization': data['customization']
    }
    
    rooms[room_code] = room_info
    players_in_rooms[host_name] = room_code
    join_room(room_code)
    
    # Send back confirmation to the frontend
    emit('room_created', {
        'roomCode': room_code, 
        'hostName': host_name, 
        'players': room_info['players']
    }, room=room_code)


# Event to join a room
@socketio.on('join_room')
def join_room_event(data):
    room_code = data['roomCode']
    player_name = data['playerName']
    
    print(f"Received join request for room: {room_code} from player: {player_name}")

    if room_code in rooms:
        rooms[room_code]['players'].append(player_name)
        join_room(room_code)

        print(f"Player {player_name} joined room {room_code}")

        # Check if all players have joined
        if len(rooms[room_code]['players']) == rooms[room_code]['num_players']:
            emit('all_players_joined', room=room_code)
        
        emit('room_joined', {
            'roomCode': room_code,
            'playerName': player_name,
            'players': rooms[room_code]['players']
        }, room=room_code)
    else:
        emit('error', {'message': 'Room not found'})
        print(f"Room {room_code} not found.")



# List of possible words (can also be customized by the host)
default_words = [
    "airplane", "umbrella", "bicycle", "computer", "telescope", "telephone", "key", 
    "sunglasses", "backpack", "guitar", "elephant", "penguin", "lion", "giraffe", 
    "kangaroo", "octopus", "turtle", "flamingo", "shark", "hedgehog", "pizza", 
    "ice cream", "hamburger", "pancakes", "sushi", "hot dog", "chocolate", 
    "apple pie", "milkshake", "popcorn", "superhero", "pirate", "wizard", "chef", 
    "astronaut", "queen", "detective", "clown", "farmer", "scientist", "beach", 
    "mountain", "castle", "amusement park", "city skyline", "desert", "jungle", 
    "school", "zoo", "space station", "rainbow", "volcano", "lightning", "snowman", 
    "treehouse", "tornado", "waterfall", "ocean", "moon", "sunflower", "running", 
    "dancing", "swimming", "climbing", "cooking", "sleeping", "flying", "painting", 
    "reading", "skipping", "dragon", "unicorn", "mermaid", "wizard’s hat", 
    "magic wand", "time machine", "robot", "alien spaceship", "haunted house", 
    "genie", "santa claus", "pumpkin", "snowflake", "easter egg", "christmas tree", 
    "fireworks", "witch hat", "candy cane", "turkey", "gift box", "roller coaster", 
    "hot air balloon", "treasure chest", "dinosaur", "ice skates", "boomerang", 
    "magic carpet", "jellyfish", "disco ball", "trampoline"
]


@socketio.on('start_game')
def start_game(data):
    room_code = data['roomCode']
    player_name = data['playerName']  # Get the player who sent the start request

    if room_code in rooms:
        # Ensure the player starting the game is the host
        if rooms[room_code]['host'] == player_name:
            # Randomly select a drawer
            players = rooms[room_code]['players']
            current_drawer = random.choice(players)
            rooms[room_code]['current_drawer'] = current_drawer
            rooms[room_code]['round_number'] = 1

            # Emit event to start the game for all players in the room
            emit('game_start', {
                'drawer': current_drawer,
                'players': players
            }, room=room_code)
        else:
            emit('error', {'message': 'Only the host can start the game'})
    else:
        emit('error', {'message': 'Room not found'})



@socketio.on('choose_word')
def choose_word(data):
    room_code = data['roomCode']
    drawer = data['drawer']

    if room_code in rooms:
        # Select 3 random words from the list (or use custom words if provided)
        word_list = rooms[room_code].get('customization', default_words)
        word_options = random.sample(word_list, 3)

        # Emit the word list to the drawer only
        emit('word_selection', {'word_options': word_options}, room=players_in_rooms[drawer])
    else:
        emit('error', {'message': 'Room not found'})


@socketio.on('submit_guess')
def handle_guess(data):
    room_code = data['roomCode']
    guess = data['guess']
    
    if room_code in rooms:
        correct_word = rooms[room_code]['current_word']
        if guess == correct_word:
            # Award points for the guesser and drawer
            # Add your scoring logic here
            emit('guess_correct', {'guesser': data['playerName']}, room=room_code)
        else:
            emit('guess_incorrect', {}, room=room_code)
    else:
        emit('error', {'message': 'Room not found'})

# Helper function to get the next drawer
def get_next_drawer(players, current_drawer):
    current_index = players.index(current_drawer)
    # Move to the next player in a circular fashion
    next_index = (current_index + 1) % len(players)
    return players[next_index]

# Example usage in the `start_next_round` function
def start_next_round(room_code):
    players = rooms[room_code]['players']
    current_drawer = rooms[room_code]['current_drawer']
    
    # Get the next drawer
    next_drawer = get_next_drawer(players, current_drawer)
    rooms[room_code]['current_drawer'] = next_drawer

    # Emit the new round start event
    emit('round_start', {'drawer': next_drawer}, room=room_code)




if __name__ == '__main__':
    socketio.run(app, debug=True)
