import {connect} from "react-redux";
import EntitiesPage from "./EntitiesPage";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.params.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EntitiesPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EntitiesPage);

export default EntitiesPageContainer;
