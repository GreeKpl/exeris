import {connect} from "react-redux";
import ActionDetails from "./ActionDetails";
import {
  fromRecipesState,
  getSelectedRecipe
} from "../../../modules/recipes";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    actionDetails: getSelectedRecipe(fromRecipesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const ActionDetailsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionDetails);

export default ActionDetailsContainer;
