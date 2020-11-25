import {connect} from "react-redux";

import React from "react";
import {Card} from "react-bootstrap";
import {fromTravelState, getTickId} from "../../../modules/travel";

class MapInfo extends React.Component {
  render() {
    return (
      <Card>
        <Card.Header>World map</Card.Header>
        <Card.Body>
          <img src={"/character/" + this.props.characterId + "/map_image?" + this.props.travelTick}
               style={{maxWidth: "100%"}}/>
        </Card.Body>
      </Card>
    );
  }
}

export {MapInfo};


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    travelTick: getTickId(fromTravelState(state, ownProps.characterId))
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const MapInfoContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MapInfo);

export default MapInfoContainer;
