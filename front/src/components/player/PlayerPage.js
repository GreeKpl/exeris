import React from "react";
import TopBarContainer from "../player/topBar/TopBarContainer";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";

class PlayerPage extends React.Component {
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
        <TopBarContainer mainPageActive={true}/>
      </div>
      <br/><br/>
      {this.props.children}
      <NotificationsContainer characterId={null}/>
    </div>;
  }
}

export default PlayerPage;
