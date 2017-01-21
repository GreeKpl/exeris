import {connect} from "react-redux";
import EntitiesList from "./EntitiesList";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EntitiesListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EntitiesList);

export default EntitiesListContainer;
