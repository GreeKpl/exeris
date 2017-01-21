import {connect} from "react-redux";
import ActionsList from "./ActionsList";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const ActionsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsList);

export default ActionsListContainer;
