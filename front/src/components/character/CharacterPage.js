import React from "react";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";
import TopBarLayout from "./../TopBarLayout";
import "./style.scss";
import CharacterDialogsContainer from "./dialogs/CharacterDialogsContainer";

class CharacterPage extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    if (this.props.characterIdsList.size === 0) {
      this.props.requestState();
    }
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
                      characterIdsList={this.props.characterIdsList}
                      activePage={this.props.pageUrl}
                      characterActivePage={this.props.characterPageUrl}
                      isSmall={this.props.isSmall}
        />
      </div>
      <div className="CharacterPage-TopBarPlaceholder"/>
      {this.props.children}
      <NotificationsContainer characterId={this.props.characterId}/>
      <CharacterDialogsContainer characterId={this.props.characterId}/>
    </div>;
  }
}

export default CharacterPage;
