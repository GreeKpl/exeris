import {connect} from "react-redux";
import EntitiesPage from "./EntitiesPage";
import {getSelectedDetails, fromEntitiesState} from "../../../modules/entities";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
    selectedDetails: getSelectedDetails(fromEntitiesState(state, ownProps.params.characterId)),
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
