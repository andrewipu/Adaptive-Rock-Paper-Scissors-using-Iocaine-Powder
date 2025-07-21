import {useState} from 'react'
import './App.css'
import Footer from './Components/Footer';
import LandingPage from './Components/LandingPage';
import GamePlayArea from './Components/GamePlayArea';
import Statistics from './Components/Statistics';

export default function App() {
  const[gameState, setGameState] = useState('landing'); // 'landing', 'playing', 'stats'
  const [finalStats, setFinalStats] = useState(null);
  // const [gameStarted, setGameStarted] = useState(false);

  //function to change game state to 'playing'
  const handleGameStart = () => setGameState('playing');

  // Called by GamePlayArea when the game ends
  const handleShowStats = (stats) => {
    setFinalStats(stats);
    setGameState('stats');
  };

  // Caled by Statitistics to go back to the Landing Page
  const handleGameEnd = () => {
    setFinalStats(null);
    setGameState('landing');
  };

  // Helper function to decide which component to render
  const renderContent = () => {
    switch (gameState) {
      case 'playing':
        return <GamePlayArea onShowStats={handleShowStats} />;
      case 'stats':
        return <Statistics stats={finalStats} onRestart={handleGameEnd} />;
      case 'landing':
      default:
        return <LandingPage startGame={handleGameStart} />;
    }
  };

  return (
    <div className='app-container'>
      {renderContent()}
      <Footer/>
    </div>
  )

  // return (
  //   <div className='app-container'>
  //     {gameStarted ?
  //     <GamePlayArea restartGame={handleGameRestart} /> :
  //     <LandingPage startGame={handleGameStart} />
  //     }
  //     <Footer/>
  //   </div>
  // );
}


















// import {useEffect, useState} from 'react'
// import './App.css'
// import Footer from './Components/Footer';
// // Icon imports...
// const arrowLeft = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/left-key-icon.svg', import.meta.url).href
// const arrowUp = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/up-key-icon.svg', import.meta.url).href
// const arrowRight = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/right-key-icon.svg', import.meta.url).href


// export default function App() {
//   const [pressedKey, setPressedKey] = useState(null)
  
//   useEffect(() => {
//     const handleKeyDown = (event) => {
//       switch(event.key) {
//         case 'ArrowUp':
//           setPressedKey('up')
//           break
//         case 'ArrowLeft':
//           setPressedKey('left')
//           break
//         case 'ArrowRight':
//           setPressedKey('right')
//           break
//       }
//     }

//     const handleKeyUp = () => {
//       setPressedKey(null)
//     }

//     //  Listen for keyboard press and release.
//     window.addEventListener('keydown', handleKeyDown)
//     window.addEventListener('keyup', handleKeyUp)

//     return () => {
//       // Remove event listeners - prevent memory leaks.
//       window.removeEventListener('keydown', handleKeyDown)
//       window.removeEventListener('keyup', handleKeyUp)
//     }
//   }, [])
  
//   return (
//     <div className = "app">
//         <div className= "description-section">
//           <h2 className='desc-title'>Adaptive Rock-Paper-Scissors Powered by IocainePowder</h2>
//           <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam pharetra sem in risus consectetur euismod. Nulla quis convallis eros. Sed ut ex nisi.
//              Donec sed semper ante. Duis ullamcorper vestibulum mauris vitae rutrum. Proin nec viverra turpis, quis suscipit lacus. Ut eu nisi elementum, porttitor nibh sit amet, finibus sem.
//               Curabitur volutpat fringilla condimentum. Quisque vehicula nulla in facilisis iaculis. Donec tincidunt at tortor vel ultricies. Sed justo mauris, lacinia et euismod nec, rutrum id dolor.
//                Etiam mi mi, imperdiet et enim nec, hendrerit fringilla nisl. Donec pharetra pellentesque arcu laoreet posuere. 
//                Maecenas pellentesque, urna tincidunt maximus rutrum, lectus mi cursus lorem, aliquam malesuada mi ligula non tortor.</p>
//         </div>
//           <div className="gameplay-sec">
//             <button className='start-game-button' type="button">Click me to play</button>
//           </div>
//           <div className='Game-controls'>
//             <div className='arrow-keys'>
//                 {/* <div className='key-display-left'> */}
//                 <div className={`key-display-left ${pressedKey === 'left' ? 'glow' : ''}`}>
//                   <img src={arrowLeft} alt="left arrow" width="80" height="80" />
//                 </div>
//                 {/* <div className='key-display-up'> */}
//                     <div className={`key-display-up ${pressedKey === 'up' ? 'glow' : ''}`}>
//                   <img src={arrowUp} alt="up arrow" width="80" height="80" />
//                   <span>ROCK</span>
//                 </div>
//               {/* <div className='key-display-right'> */}
//               <div className={`key-display-right ${pressedKey === 'right' ? 'glow' : ''}`}>
//                 <img src={arrowRight} alt="right arrow" width="80" height="80" />
//               </div>
//             </div>
//             <div className='controls-instructions-text'>
//               <p>Use arrow keys to play the game! UP (Rock), Left (Paper), Right (Scissors). Press “ESC”/Escape to end the game </p>
//             </div>
//             <div className='Restart-button-sec'>
//               <button className='Restart-game-button' type='button'>Restart</button>
//             </div>
            
//           </div>
//         <Footer/>
//     </div> 
//   )
// }




