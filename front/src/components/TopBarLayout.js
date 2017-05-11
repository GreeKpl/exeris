import React from "react";
import TopBarContainer from "./player/topBar/TopBarContainer";
import CharacterTopBarContainer from "./character/topBar/CharacterTopBarContainer";
import MobileCharacterTopBarContainer from "./character/topBar/MobileCharacterTopBarContainer";


const TopBarLayout = ({characterId, activePage, characterActivePage, isSmall}) => {
  return <div>
    {isSmall ?
      <MobileCharacterTopBarContainer characterId={characterId}
                                      activePage={activePage}
                                      characterActivePage={characterActivePage}/>
      : [
        <TopBarContainer key="topBar" characterId={characterId}
                         activePage={activePage}/>,
        <CharacterTopBarContainer key="characterTopBar" characterId={characterId}
                                  activePage={characterActivePage}/>
      ]}
  </div>;
};

export default TopBarLayout;
