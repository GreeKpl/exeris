import {connect} from "react-redux";
import ActionDetails from "./ActionDetails";
import {
  fromRecipesState,
  getSelectedRecipe,
  createActivityFromRecipe
} from "../../../modules/recipes";
import {getFormValues} from "redux-form/immutable";


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    recipeDetails: getSelectedRecipe(fromRecipesState(state, ownProps.characterId)),
    formState: getFormValues('recipeDetails')(state),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSubmit: data => {
      dispatch(createActivityFromRecipe(ownProps.characterId, data.toJS()));
    },
  }
};

const ActionDetailsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionDetails);

export default ActionDetailsContainer;
