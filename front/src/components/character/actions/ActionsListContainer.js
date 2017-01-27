import {connect} from "react-redux";
import ActionsList from "./ActionsList";
import {
  getFilteredRecipes,
  fromRecipesState,
  requestRecipesList,
  selectRecipe
} from "../../../modules/recipes";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    actionsList: getFilteredRecipes(fromRecipesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSelectAction: actionId =>
      dispatch(selectRecipe(ownProps.characterId, actionId)),
    requestState: () => dispatch(requestRecipesList(ownProps.characterId))
  }
};

const ActionsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsList);

export default ActionsListContainer;
