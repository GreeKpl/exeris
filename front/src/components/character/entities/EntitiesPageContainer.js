import {connect} from "react-redux";
import {getSelectedDetails, fromEntitiesState} from "../../../modules/entities";

import React from "react";
import {Grid, Row, Col, Tabs, Tab} from "react-bootstrap";
import EntitiesListContainer from "./EntitiesListContainer";
import MapInfoContainer from "./MapInfoContainer";
import ControlMovementContainer from "./ControlMovementContainer";
import ActionsBarContainer from "../../commons/entityActions/ActionsBarContainer";
import {EntityDetailsContainer, ActivityDetailsContainer} from "./EntityDetailsContainer";

export class EntitiesPage extends React.Component {
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

    if (this.props.isSmall) {
      return (
        <div>
          <Tabs bsStyle="tabs" className="TripleNavTabsContainer" defaultActiveKey={1}>
            <Tab eventKey={1} title="List">
              <EntitiesListContainer characterId={this.props.characterId}/>
            </Tab>
            <Tab eventKey={3} title="Map">
              <MapInfoContainer characterId={this.props.characterId}/>
              <ControlMovementContainer characterId={this.props.characterId}/>
            </Tab>
            <Tab eventKey={2} title="Info">
              {optionalEntityInfo}
            </Tab>
          </Tabs>
          <ActionsBarContainer characterId={this.props.characterId}/>
        </div>);
    } else {
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
}


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
    selectedDetails: getSelectedDetails(fromEntitiesState(state, ownProps.params.characterId)),
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EntitiesPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EntitiesPage);

export default EntitiesPageContainer;
