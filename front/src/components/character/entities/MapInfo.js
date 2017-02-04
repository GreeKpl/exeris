import React from "react";
import {Panel} from "react-bootstrap";

class MapInfo extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Panel header="World map">
        <img src={"/character/" + this.props.characterId + "/map_image"} style={{maxWidth: "100%"}}/>
      </Panel>);
  }
}

export default MapInfo;
