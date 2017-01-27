import {
  recipesReducer,
  decoratedRecipesReducer,
  fromRecipesState,
  updateFilterText,
  getFilteredRecipes,
  getAllRecipes,
  updateRecipesList,
  getFilterText,
  setSelectedRecipe
} from "../../src/modules/recipes";
import * as Immutable from "immutable";

describe('(recipes) recipesReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(recipesReducer(undefined, {})).to.equal(Immutable.fromJS({
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
    expect(state).to.equal(previousState);
  });

  it('Should update the filter text when a new filter text is supplied.', () => {
    const previousState = Immutable.fromJS({
      "filter": "",
      "list": [],
      "selectedRecipe": {},
    });
    let state = recipesReducer(previousState, updateFilterText(0, "hehe"));
    expect(state).to.equal(previousState.set("filter", "hehe"));
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
    expect(state).to.equal(Immutable.fromJS({
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
    expect(getFilterText(fromRecipesState(globalState, "DEF"))).to.equal("forg");
    expect(getAllRecipes(fromRecipesState(globalState, "DEF"))).to.equal(Immutable.fromJS(recipesList));
    expect(getFilteredRecipes(fromRecipesState(globalState, "DEF"))).to.equal(Immutable.fromJS([
      {id: 1, name: "forging a sword"},
    ]));
  });
});