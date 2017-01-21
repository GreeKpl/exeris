import {connect} from "react-redux";
import ActionDetails from "./ActionDetails";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const ActionDetailsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionDetails);

export default ActionDetailsContainer;
