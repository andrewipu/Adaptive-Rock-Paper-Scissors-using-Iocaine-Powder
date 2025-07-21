import {useEffect} from 'react';
import '../App.css';
import Description from './Description';
import GameControls from './GameControls';
// Icon imports...
// const arrowLeft = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/left-key-icon.svg', import.meta.url).href
// const arrowUp = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/up-key-icon.svg', import.meta.url).href
// const arrowRight = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/right-key-icon.svg', import.meta.url).href

export default function LandingPage ({startGame}) {
  //listed for the "Enter" key press
  useEffect (() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Enter') {
        startGame();
      }
    };

    // Add event listener when component is shown
    window.addEventListener('keydown', handleKeyDown);

    //clean up event listener
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    }
  }, [startGame]); //
  

    return (
      <main className = "content">
                <Description/>
                <div className="gameplay-sec">
                  <button className='start-game-button' type="button" onClick={startGame}>Click me to play</button>
                </div>
                <GameControls showRestart={false}/>
          </main> 
        )
}