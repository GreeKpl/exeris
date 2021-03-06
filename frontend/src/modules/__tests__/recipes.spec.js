import {
  recipesReducer,
  decoratedRecipesReducer,
  fromRecipesState,
  updateFilterText,
  getFilteredRecipes,
  getAllRecipes,
  updateRecipesList,
  getFilterText,
  setSelectedRecipe,
  __RewireAPI__ as recipesRewire, requestRecipesList, UPDATE_RECIPES_LIST, selectRecipe, SET_SELECTED_RECIPE,
  CLEAR_SELECTED_RECIPE, createActivityFromRecipe
} from "../recipes";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../../../tests/testUtils";

describe('(recipes) recipesReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(recipesReducer(undefined, {})).toEqual(Immutable.fromJS({
      "filter": "",
      "list": [],
      "selectedRecipe": {},
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      "filter": "",
      "list": [],
      "selectedRecipe": {},
    });
    let state = recipesReducer(previousState, {});
    expect(state).toEqual(previousState);
  });

  it('Should update the filter text when a new filter text is supplied.', () => {
    const previousState = Immutable.fromJS({
      "filter": "",
      "list": [],
      "selectedRecipe": {},
    });
    let state = recipesReducer(previousState, updateFilterText(0, "hehe"));
    expect(state).toEqual(previousState.set("filter", "hehe"));
  });

  it('Should update the selected recipe.', () => {
    const previousState = Immutable.fromJS({
      "filter": "",
      "list": [],
      "selectedRecipe": {},
    });
    let state = recipesReducer(previousState, setSelectedRecipe(0, {
      id: 1,
      name: "forging a sword",
    }));
    expect(state).toEqual(Immutable.fromJS({
      "filter": "",
      "list": [],
      "selectedRecipe": {
        id: 1,
        name: "forging a sword",
      },
    }));
  });

  it('Should update the speech of a specified character.', () => {
    let state = decoratedRecipesReducer(undefined, {});
    const recipesList = [
      {id: 1, name: "forging a sword"},
      {id: 2, name: "building a hut"},
      {id: 3, name: "building a ship"},
    ];
    state = decoratedRecipesReducer(state, updateRecipesList("DEF", recipesList));
    state = decoratedRecipesReducer(state, updateFilterText("DEF", "forg"));

    const globalState = Immutable.Map({recipes: state});
    expect(getFilterText(fromRecipesState(globalState, "DEF"))).toEqual("forg");
    expect(getAllRecipes(fromRecipesState(globalState, "DEF"))).toEqual(Immutable.fromJS(recipesList));
    expect(getFilteredRecipes(fromRecipesState(globalState, "DEF"))).toEqual(Immutable.fromJS([
      {id: 1, name: "forging a sword"},
    ]));
  });


  describe("Asynchronous socketio actions", () => {
    const charId = "DEF";

    it('Should request the recipes list.', () => {
      const recipesList = [{
        id: "ABE",
        name: "A new recipe",
      }];

      const store = createMockStore({}, [recipesList]);

      store.dispatch(requestRecipesList(charId));
      store.socketCalledWith("character.get_all_recipes", charId);

      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual({
        type: UPDATE_RECIPES_LIST,
        recipesList: recipesList,
        characterId: charId,
      });
    });

    it('Should request the recipes list.', () => {
      const recipeId = "ALA123";
      const recipeDetails = {
        id: recipeId,
        name: "some recipe name",
        required: "yes",
      };
      const store = createMockStore({}, [recipeDetails]);

      store.dispatch(selectRecipe(charId, recipeId));
      store.socketCalledWith("character.get_recipe_details", charId, recipeId);

      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual({
        type: SET_SELECTED_RECIPE,
        recipeDetails: recipeDetails,
        characterId: charId,
      });
    });

    it('Should request to create an activity from a recipe.', () => {
      const recipeId = "ALA123";
      const activitySubjectId = "ENTITY_ID";
      const recipeFormStateWithoutSubject = {
        otherParams: "otherParams",
      };
      const recipeFormStateWithSubject = {
        activitySubject: activitySubjectId,
        ...recipeFormStateWithoutSubject,
      };
      const recipeDetails = {
        id: recipeId,
        name: "some recipe name",
        required: "yes",
      };

      const store = createMockStore(Immutable.fromJS({
        recipes: {
          [charId]: {
            selectedRecipe: recipeDetails,
          },
        }
      }), [recipeFormStateWithSubject]);


      store.dispatch(createActivityFromRecipe(charId, recipeFormStateWithSubject));
      store.socketCalledWith("character.create_activity_from_recipe", charId,
        recipeId, recipeFormStateWithoutSubject, activitySubjectId);

      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual({
        type: CLEAR_SELECTED_RECIPE,
        characterId: charId,
      });
    });
  });
});
