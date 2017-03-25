import {connect} from "react-redux";
import ControlMovement from "./ControlMovement";
import {
  canBeControlled,
  fromTravelState,
  changeMovementDirection,
  stopMovement,
  getMovementAction,
  requestTravelState
} from "../../../modules/travel";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    canBeControlled: canBeControlled(fromTravelState(state, ownProps.characterId)),
    movementAction: parseHtmlToComponents(ownProps.characterId,
      getMovementAction(fromTravelState(state, ownProps.characterId))),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSubmitDirection: direction => {
      dispatch(changeMovementDirection(ownProps.characterId, direction));
    },
    onSubmitStop: () => {
      dispatch(stopMovement(ownProps.characterId));
    },
    requestState: () => {
      dispatch(requestTravelState(ownProps.characterId));
    },
  }
};

const ControlMovementContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ControlMovement);

export default ControlMovementContainer;
