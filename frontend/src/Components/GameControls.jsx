import { useState, useEffect } from 'react';
import '../App.css';

// Icon imports...
const arrowLeft = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/left-key-icon.svg', import.meta.url).href;
const arrowUp = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/up-key-icon.svg', import.meta.url).href;
const arrowRight = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/right-key-icon.svg', import.meta.url).href;

const checkIcon = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/check-solid.svg', import.meta.url).href;
const crossIcon = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/circle-xmark-regular.svg', import.meta.url).href;
const dashIcon = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/minus-solid.svg', import.meta.url).href;


export default function GameControls({ showRestart, onRestart, onUserMove }) {
    const [pressedKey, setPressedKey] = useState(null);

    useEffect(() => {
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                onRestart(); // Call the restart function when Escape is pressed
                return;
            }
            if (event.repeat) return; // Ignore holding down a key

            let move = null;

            switch (event.key) {
                case 'ArrowUp':
                    setPressedKey('up');
                    move = 'rock';
                    break;
                case 'ArrowLeft':
                    setPressedKey('left');
                    move = 'paper';
                    break;
                case 'ArrowRight':
                    setPressedKey('right');
                    move = 'scissors';
                    break;
            }
            // If a valid move is detected, call the onUserMove callback
            // This allows the parent component to handle the user's move
            if (move && onUserMove) {
                onUserMove(move);
            }
        };

        const handleKeyUp = () => {
            setPressedKey(null);
        };

        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    }, [onUserMove, onRestart]);

    return (
        <div className='Game-controls'>
            <div className='arrow-keys'>
                <div className={`key-display-left ${pressedKey === 'left' ? 'glow' : ''}`}>
                    <img src={arrowLeft} alt="left arrow" width="80" height="80" />
                </div>
                <div className={`key-display-up ${pressedKey === 'up' ? 'glow' : ''}`}>
                    <img src={arrowUp} alt="up arrow" width="80" height="80" />
                </div>
                <div className={`key-display-right ${pressedKey === 'right' ? 'glow' : ''}`}>
                    <img src={arrowRight} alt="right arrow" width="80" height="80" />
                </div>
            </div>
            <div className='controls-instructions-text'>
                <p>Use arrow keys to play the game! UP (Rock), Left (Paper), Right (Scissors). Press “ESC”/Escape to end the game </p>
            </div>
            {/* {showRestart && (
                <div className='Restart-button-sec'>
                    <button className='Restart-game-button' type='button' onClick={onRestart}>Restart</button>
                </div>
            )} */}
            {showRestart ? (
                <div className='Restart-button-sec'>
                    <button className='Restart-game-button' type='button' onClick={onRestart}>Restart</button>
                </div>
            ) : (
                // --- Replace the old <p> tag with this block ---
                <div className='icon-definitions'>
                    <p>Won round =</p>
                    <span>
                        <img src={checkIcon} width="20" height="20" className='icon-def-win'/>
                    </span>
                    <p>Lost round =</p>
                    <span >
                        <img src={crossIcon} width="20" height="20" className='icon-def-lose'/>
                    </span>
                    <p>Tie =</p>
                    <span >
                        <img src={dashIcon} width="20" height="20" className='icon-def-tie'/>
                    </span>

                    {/* <span>Won round = 
                        <img src={checkIcon} width="20" height="20" className='icon-def-win'/>
                    </span> */}
                    {/* <span >Lost round = 
                        <img src={crossIcon} width="20" height="20" className='icon-def-lose'/>
                    </span>
                    <span >Tie = 
                        <img src={dashIcon} width="20" height="20" className='icon-def-tie'/>
                    </span> */}
                </div>
            )}
        </div>
    );
}