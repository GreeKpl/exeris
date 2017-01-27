import {connect} from "react-redux";
import ActionsFilter from "./ActionsFilter";
import {
  getFilterText,
  fromRecipesState,
  updateFilterText
} from "../../../modules/recipes";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    filterText: getFilterText(fromRecipesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onChange: event => dispatch(updateFilterText(ownProps.characterId, event.target.value)),
  }
};

const ActionsFilterContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsFilter);

export default ActionsFilterContainer;
