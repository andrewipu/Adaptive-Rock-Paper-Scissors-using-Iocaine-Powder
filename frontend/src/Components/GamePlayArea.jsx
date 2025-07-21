import {useState, useEffect, useRef} from 'react'; 
import '../App.css'
import Description from './Description';
import GameControls from './GameControls';

//icon import
const checkIcon = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/check-solid.svg', import.meta.url).href;
const crossIcon = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/circle-xmark-regular.svg', import.meta.url).href;
const dashIcon = new URL('C:/VS Code/Rock-Paper-Scissors using Iocaine Powder/Web App/frontend/src/assets/minus-solid.svg', import.meta.url).href;

//helper function for displaying result icons.
const ResultIcon = ({result}) => {
  if (result === 'win') return <span className='result-icon-win'>
    <img src={checkIcon} width="20" height="20"/>
  </span>;
  if (result === 'lose') return <span className='result-icon-lose'>
    <img src={crossIcon} width="20" height="20"/>
  </span>;
  if (result === 'tie') return <span className='result-icon-tie'>
    <img src={dashIcon} width="20" height="20"/>
  </span>;
  return null;
}

export default function GamePlayArea({onShowStats}) {
  // const [message, setMessage] = useState('Key in your move...');
  const [isLoading, setIsLoading] = useState(false);
  const [scores, setScores] = useState({user:0, bot:0});
  const [history, setHistory] = useState([]); //state to hold list of all rounds.
  const historyContainerRef = useRef(null); //Ref for scrolling container.

  //Scroll to bottom of history list when new item is added.
  useEffect (() => {
    if (historyContainerRef.current) {
      const {scrollHeight} = historyContainerRef.current;
      historyContainerRef.current.scrollTo({top: scrollHeight, behavior: 'smooth'});
    }
  }, [history]);


  const determineWinner = (playerMove, computerMove) => {
    if (playerMove === computerMove) return 'tie';
        if (
            (playerMove === 'rock' && computerMove === 'scissors') ||
            (playerMove === 'scissors' && computerMove === 'paper') ||
            (playerMove === 'paper' && computerMove === 'rock')
        ) {
            return 'win';
        }
        return 'lose';
  };

  const handleUserMove = async (move) => {
    //If a request is already in progress, don't do anything.
    if (isLoading) return;

    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST', //POST because, we are sending data to the server
        headers: {'Content-Type': 'application/json'},//inform server that we are sending JSON data
        body: JSON.stringify({ move: move }), // convert the data to JSON string
      });

      // check if the response is ok
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json(); // await because we are waiting for the response to be converted to JSON
      const botChoice = data.bot_move;
      const result = determineWinner(move, botChoice);

      // Update scores
      if (result === 'win') setScores(prev => ({ ...prev, user: prev.user + 1 }));
      if (result === 'lose') setScores(prev => ({ ...prev, bot: prev.bot + 1 }));

      // Create a new history entry
      const newHistoryEntry = {
          round: history.length + 1,
          botMove: botChoice,
          result: result,
      };

      // Add the new entry to the history state
      setHistory(prev => [...prev, newHistoryEntry]);

    } catch (error) {
      console.error('Failed to fetch bot\'s move:', error);
    } finally {
      setTimeout(() => setIsLoading(false), 500); //short pause
    }
  };

  //Function responsible for ending the game and fetching stats
  const handleRestart = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/reset', {method: 'POST'});
      if (!response.ok) {
        throw new Error (`Server error: ${response.status}`);
      }
      const finalStats = await response.json();
      onShowStats(finalStats); // pass fetched stats to App component
    } catch (error) {
      console.error("Failed to get stats:", error);
      //If the API fails, show stats with null data
      onShowStats(null);
    }
  };

    return (
      <main className='content'>
            <Description />
            <div className='gameplay-box'>
                <div className='score-display'>
                    <span><b>Your Score: </b>{scores.user}</span>
                    <span><b>Bot Score: </b>{scores.bot}</span>
                </div>

                {/* This is the new scrolling round history display */}
                <div className="round-history-container" ref={historyContainerRef}>
                    {history.length === 0 ? (
                        <p className="history-placeholder">Key in your move to start...</p>
                    ) : (
                        history.map((item) => (
                            <div key={item.round} className="round-item">
                                <span><b>Round {item.round}: </b>Iocaine plays {item.botMove}</span>
                                <ResultIcon result={item.result} />
                            </div>
                        ))
                    )}
                </div>
            </div>
            <GameControls
                showRestart={true}
                onRestart={handleRestart}
                onUserMove={handleUserMove}
            />
        </main>
    )
}