import React from "react";
import {Grid, Row, Col, Panel} from "react-bootstrap";
import EntitiesListContainer from "./EntitiesListContainer";
import MapInfoContainer from "./MapInfoContainer";
import ControlMovementContainer from "./ControlMovementContainer";

class EventsPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Grid fluid={true}>
        <Row>
          <Col xs={12} md={7}>
            <Panel header="Your RootLocation">
              <EntitiesListContainer characterId={this.props.characterId}/>
            </Panel>
            <Panel header="Other RootLocation">
              <EntitiesListContainer characterId={this.props.characterId}/>
            </Panel>
          </Col>
          <Col xs={12} md={5}>
            <MapInfoContainer characterId={this.props.characterId}/>
            <ControlMovementContainer characterId={this.props.characterId}/>
          </Col>
        </Row>
      </Grid>);
  }
}

export default EventsPage;
