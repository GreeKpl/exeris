import {ownCharactersListReducer, playerReducer} from "../../src/player/reducers";
import * as Immutable from "immutable";
import {UPDATE_OWN_CHARACTERS_LIST, UPDATE_ACHIEVEMENTS_LIST} from "../../src/player/actions";

describe('(player) ownCharactersListReducer', () => {

  it('Should be a function.', () => {
    expect(ownCharactersListReducer).to.be.a('function')
  });

  it('Should initialize with initial state of empty list.', () => {
    expect(ownCharactersListReducer(undefined, {})).to.equal(Immutable.List());
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.List.of({id: 1, name: "john"}, {id: 7, name: "ally"});
    let state = ownCharactersListReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update the state if empty list is supplied.', () => {
    const previousState = Immutable.List.of({id: 1, name: "john"}, {id: 7, name: "ally"});
    let state = ownCharactersListReducer(previousState, {
      type: UPDATE_OWN_CHARACTERS_LIST,
      charactersList: [],
    });
    expect(state).to.equal(Immutable.List());
  });

  it('Should update the state if new list is supplied.', () => {
    const previousState = Immutable.List.of({id: 1, name: "john"}, {id: 7, name: "ally"});
    let state = ownCharactersListReducer(previousState, {
      type: UPDATE_OWN_CHARACTERS_LIST,
      charactersList: [{id: 11, name: "ad"}],
    });
    expect(state).to.equal(Immutable.List.of(Immutable.Map({id: 11, name: "ad"})));
  });
});


describe('(player) playerReducer', () => {

  it('Should be a function.', () => {
    expect(playerReducer).to.be.a('function')
  });

  it('Should initialize with initial state of empty list.', () => {
    expect(playerReducer(undefined, {})).to.equal(Immutable.fromJS({"achievements": []}));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.Map({achievements: []});
    let state = playerReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update the state.', () => {
    const previousState = Immutable.Map({achievements: Immutable.List()});
    let state = playerReducer(previousState, {
      type: UPDATE_ACHIEVEMENTS_LIST,
      achievementsList: [{title: "abc", content: "be able to read abc"}],
    });
    expect(state).to.equal(Immutable.fromJS({
      achievements: [{title: "abc", content: "be able to read abc"}]
    }));
  });
});
