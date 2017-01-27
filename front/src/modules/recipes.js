import * as Immutable from "immutable";
import {characterReducerDecorator} from "../util/characterReducerDecorator";
import socket from "../util/server";

export const SET_SELECTED_RECIPE = "exeris-front/recipes/SET_SELECTED_RECIPE";
export const UPDATE_RECIPES_LIST = "exeris-front/recipes/UPDATE_RECIPES_LIST";
export const UPDATE_FILTER_TEXT = "exeris-front/recipes/UPDATE_FILTER_TEXT";
export const CLEAR_SELECTED_RECIPE = "exeris-front/recipes/CLEAR_SELECTED_RECIPE";


export const updateFilterText = (characterId, filterText) => {
  return {
    type: UPDATE_FILTER_TEXT,
    filterText: filterText,
    characterId: characterId,
  };
};

export const requestRecipesList = characterId => {
  return dispatch =>
    socket.request("character.get_all_recipes", characterId, recipesList =>
      dispatch(updateRecipesList(characterId, recipesList)));
};

export const updateRecipesList = (characterId, recipesList) => {
  return {
    type: UPDATE_RECIPES_LIST,
    recipesList: recipesList,
    characterId: characterId,
  }
};

export const selectRecipe = (characterId, recipeId) => {
  return dispatch => {
    socket.request("character.get_recipe_details", characterId, recipeId, (recipeDetails) => {
      dispatch(setSelectedRecipe(characterId, recipeDetails));
    });
  };
};

export const createActivityFromRecipe = (characterId, recipeFormState) => {
  return (dispatch, getState) => {
    const selectedRecipe = getSelectedRecipe(fromRecipesState(getState(), characterId));
    const recipeId = selectedRecipe.get("id");
    const subjectEntityId = recipeFormState.activitySubject;
    let recipeFormStateCopy = {...recipeFormState};
    delete recipeFormStateCopy.activitySubject;

    socket.request("character.create_activity_from_recipe", characterId,
      recipeId, recipeFormStateCopy, subjectEntityId,
      () => dispatch(clearSelectedRecipe(characterId)));
  }
};

export const clearSelectedRecipe = characterId => {
  return {
    type: CLEAR_SELECTED_RECIPE,
    characterId: characterId,
  };
};

export const setSelectedRecipe = (characterId, recipeDetails) => {
  return {
    type: SET_SELECTED_RECIPE,
    recipeDetails: recipeDetails,
    characterId: characterId,
  };
};

export const recipesReducer = (state = Immutable.fromJS({
  "filter": "",
  "list": [],
  "selectedRecipe": {},
  "formState": {},
}), action) => {
  switch (action.type) {
    case UPDATE_FILTER_TEXT:
      return state.set("filter", action.filterText);
    case UPDATE_RECIPES_LIST:
      return state.set("list", Immutable.fromJS(action.recipesList));
    case SET_SELECTED_RECIPE:
      return state.set("selectedRecipe", Immutable.fromJS(action.recipeDetails));
    case CLEAR_SELECTED_RECIPE:
      return state.set("selectedRecipe", Immutable.Map());
    default:
      return state;
  }
};

export const decoratedRecipesReducer = characterReducerDecorator(recipesReducer);

export const getFilterText = state => state.get("filter", "");

export const getAllRecipes = state => state.get("list", Immutable.List());

export const getFilteredRecipes = state => getAllRecipes(state)
  .filter(recipe => recipe.get("name")
    .indexOf(getFilterText(state)) !== -1);

export const getSelectedRecipe = state => state.get("selectedRecipe", Immutable.Map());

export const fromRecipesState = (state, characterId) =>
  state.getIn(["recipes", characterId], Immutable.Map());
