import React from "react";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";
import TopBarLayoutContainer from "./../TopBarLayoutContainer";

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
        <TopBarLayoutContainer characterId={this.props.characterId}
                               activePage={this.props.pageUrl}
                               characterActivePage={this.props.characterPageUrl}
        />
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
