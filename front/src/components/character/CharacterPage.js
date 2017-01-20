import React from "react";
import TopBarContainer from "../player/topBar/TopBarContainer";
import CharacterTopBarContainer from "../character/topBar/CharacterTopBarContainer";

class CharacterPage extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return <div>
      <div style={{
        position: "fixed",
        top: "0px",
        left: "0px",
        right: "0px",
      }}>
        <TopBarContainer characterId={this.props.characterId}/>
        <CharacterTopBarContainer characterId={this.props.characterId}/>
      </div>
      <br/><br/>
      <br/><br/>
      {this.props.children}
    </div>;
  }
}

export default CharacterPage;
