import React from "react";
import {Panel} from "react-bootstrap";

class EventsPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return <Panel header="Events list">
      Events page for {this.props.characterId}.
    </Panel>;
  }
}

export default EventsPage;
