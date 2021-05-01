import React from "react";
import TopBarContainer from "./player/topBar/TopBarContainer";
import CharacterTopBarContainer from "./character/topBar/CharacterTopBarContainer";
import MobileCharacterTopBarContainer from "./character/topBar/MobileCharacterTopBarContainer";


const TopBarLayout = ({characterId, activePage, characterActivePage, isSmall, characterIdsList}) => {
  return <div>
    {isSmall ?
      <MobileCharacterTopBarContainer characterId={characterId}
                                      characterIdsList={characterIdsList}
                                      activePage={activePage}
                                      characterActivePage={characterActivePage}/>
      : [
        <TopBarContainer key="topBar"
                         characterId={characterId}
                         characterIdsList={characterIdsList}
                         activePage={activePage}/>,
        <CharacterTopBarContainer key="characterTopBar" characterId={characterId}
                                  activePage={characterActivePage}/>
      ]}
  </div>;
};

export default TopBarLayout;
