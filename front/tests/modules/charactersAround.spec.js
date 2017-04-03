import {
  updateCharactersAround,
  charactersAroundReducer,
  getIdsOfCharactersAround,
  fromCharactersAroundState,
  decoratedCharactersAroundReducer
} from "../../src/modules/charactersAround";
import * as Immutable from "immutable";

describe('(charactersAround) charactersAroundReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(charactersAroundReducer(undefined, {})).to.equal(Immutable.List());
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS([{id: 1, name: "john"}]);
    let state = charactersAroundReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update the charactersAround if an empty list is supplied.', () => {
    const previousState = Immutable.fromJS(
      [{id: 1, name: "john"}],
    );
    let state = charactersAroundReducer(previousState, updateCharactersAround(0, []));
    expect(state).to.equal(Immutable.List());
  });

  it('Should replace the state if a new list is supplied.', () => {
    const previousState = Immutable.fromJS(
      [{id: 1, name: "john"}],
    );
    let state = charactersAroundReducer(previousState, updateCharactersAround(0, [{id: 7, name: "ade"}]));
    expect(state).to.equal(Immutable.fromJS([{id: 7, name: "ade"}]));
  });

  it('Should update the charactersAround of a specified character.', () => {
    let state = decoratedCharactersAroundReducer(undefined, {});
    state = decoratedCharactersAroundReducer(state, updateCharactersAround("DEF", ["HEH", "AHA"]));
    state = decoratedCharactersAroundReducer(state, updateCharactersAround("3", ["HEJ", "HON"]));
    state = Immutable.Map({charactersAround: state});
    expect(getIdsOfCharactersAround(fromCharactersAroundState(state, "3")))
      .to.equal(Immutable.List(["HEJ", "HON"]));
    expect(getIdsOfCharactersAround(fromCharactersAroundState(state, "DEF")))
      .to.equal(Immutable.List(["HEH", "AHA"]));
  });
});
