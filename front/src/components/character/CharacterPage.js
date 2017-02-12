import React from "react";
import TopBarContainer from "../player/topBar/TopBarContainer";
import CharacterTopBarContainer from "../character/topBar/CharacterTopBarContainer";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";

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
        zIndex: 1,
      }}>
        <TopBarContainer characterId={this.props.characterId}/>
        <CharacterTopBarContainer characterId={this.props.characterId} activePage={this.props.characterPageUrl}/>
      </div>
      <br/><br/>
      <br/><br/>
      <br/>
      {this.props.children}
      <NotificationsContainer characterId={this.props.characterId}/>
    </div>;
  }
}

export default CharacterPage;
