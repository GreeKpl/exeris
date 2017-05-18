import React from "react";
import {Grid, Row, Col, Panel} from "react-bootstrap";
import EntitiesListContainer from "./EntitiesListContainer";
import MapInfoContainer from "./MapInfoContainer";
import ControlMovementContainer from "./ControlMovementContainer";
import ActionsBarContainer from "../../commons/entityActions/ActionsBarContainer";
import {EntityDetailsContainer, ActivityDetailsContainer} from "./EntityDetailsContainer";

class EntitiesPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {

    let optionalEntityInfo = null;
    if (this.props.selectedDetails) {
      switch (this.props.selectedDetails.get("type")) {
        case "Activity":
          optionalEntityInfo = <ActivityDetailsContainer characterId={this.props.characterId}/>;
          break;
        default:
          optionalEntityInfo = <EntityDetailsContainer characterId={this.props.characterId}/>;
      }
    }

    return (
      <div>
        <Grid fluid={true}>
          <Row>
            <Col xs={12} md={7}>
              <EntitiesListContainer characterId={this.props.characterId}/>
            </Col>
            <Col xs={12} md={5}>
              {optionalEntityInfo}
              <MapInfoContainer characterId={this.props.characterId}/>
              <ControlMovementContainer characterId={this.props.characterId}/>
            </Col>
          </Row>
        </Grid>
        <ActionsBarContainer characterId={this.props.characterId}/>
      </div>);
  }
}

export default EntitiesPage;
