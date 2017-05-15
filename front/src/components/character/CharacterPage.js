import React from "react";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";
import TopBarLayout from "./../TopBarLayout";

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
        <TopBarLayout characterId={this.props.characterId}
                      activePage={this.props.pageUrl}
                      characterActivePage={this.props.characterPageUrl}
                      isSmall={this.props.isSmall}
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
