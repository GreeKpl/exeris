import {connect} from "react-redux";
import ControlMovement from "./ControlMovement";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const ControlMovementContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ControlMovement);

export default ControlMovementContainer;
