import React from 'react';
import '../App.css';

export default function Description() {
    return (
        <div className= "description-section">
                <h2 className='desc-title'>Adaptive Rock-Paper-Scissors Powered by Iocaine Powder</h2>
                <p className='description-content'>Rock-Paper-Scissors (RPS) isn't just a game of chance — it's a game of strategy and psychological insight. 
                    In real-world scenarios, success often hinges on reading and exploiting human behavioral patterns. While humans aren't able to play completely random,
                     a purely random strategy is the best strategy to bring to a RPS game. It’s unexploitable because no patterns can be predicted from it. 
                     At the heart of this program lies the Iocaine Powder algorithm, developed by Dan Egnor in 1999. It's a heuristically designed compilation of strategies
                     and meta-strategies that aim to predict the opponent's move. Originally designed to compete against other bots, it was never formally tested against humans — until now. 
                     Iocaine Powder combines a suite of predictive strategies and meta-strategies that adapt dynamically to an opponent's behavior. 
                     It may not win every round, but over the course of a match, it aims to come out on top more often than not. Read more about Iocaine <a href="https://web.archive.org/web/20110723203327/http://www.ofb.net/~egnor/iocaine.html">here.</a></p>
              </div>
    );
}

