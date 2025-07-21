// import {useEffect, useState} from 'react'
// import { useState } from 'react'; 
import '../App.css'
import Description from './Description';
import GameControls from './GameControls';

export default function Statistics({stats, onRestart}) {

    

    // Error handling in case of no stats
    if (!stats) {
        return (
            <main className='content'>
                <Description />
                <div className='statistics-box'>
                    <h3 className='no-stats-title'>Could not load statistics.</h3>
                </div>
                <GameControls 
                    showRestart={true} 
                    onRestart={onRestart} />
            </main>
        );
    }

    const { rounds, user_wins, bot_wins, ties, user_rock, user_paper, user_scissors } = stats;

    let winMessage = "The game is a draw!";
    if (user_wins > bot_wins) {
        winMessage = "You win!";
    } else if (bot_wins > user_wins) {
        winMessage = "IocaineBot wins!";
    }

    return (
        <main className="content">
            <Description />
            <div className='statistics-box'>
                <div className='stats-summary'>
                    <h3 className='win-lose-title'>{winMessage}</h3>
                    <p>Total Rounds: {rounds}</p>
                    <p>Your wins: {user_wins}</p>
                    <p>IocaineBot wins: {bot_wins}</p>
                    <p>Ties: {ties}</p>
                </div>
                <div className='stats-moves'>
                    <h4 className='moves-title'>Your Move Distribution:</h4>
                    <p>Rock: {user_rock}</p>
                    <p>Paper: {user_paper}</p>
                    <p>Scissors: {user_scissors}</p>
                </div>
            </div>
            <GameControls showRestart={true} onRestart={onRestart} />
        </main>
    );
}