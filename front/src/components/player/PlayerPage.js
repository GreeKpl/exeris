import React from "react";
import TopBarContainer from "../player/topBar/TopBarContainer";

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
      }}>
        <TopBarContainer/>
      </div>
      <br/><br/>
      {this.props.children}
    </div>;
  }
}

export default PlayerPage;
