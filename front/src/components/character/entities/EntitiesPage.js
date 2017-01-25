import React from "react";
import {Grid, Row, Col, Panel} from "react-bootstrap";
import EntitiesListContainer from "./EntitiesListContainer";
import MapInfoContainer from "./MapInfoContainer";
import ControlMovementContainer from "./ControlMovementContainer";
import ActionsBarContainer from "./ActionsBarContainer";
import "./style.scss";

class EventsPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        <Grid fluid={true}>
          <Row>
            <Col xs={12} md={7}>
              <EntitiesListContainer characterId={this.props.characterId}/>
            </Col>
            <Col xs={12} md={5}>
              <MapInfoContainer characterId={this.props.characterId}/>
              <ControlMovementContainer characterId={this.props.characterId}/>
            </Col>
          </Row>
        </Grid>
        <ActionsBarContainer characterId={this.props.characterId}/>
      </div>);
  }
}

export default EventsPage;
